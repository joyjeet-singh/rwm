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
    python scripts/t1_bibliography.py --verify --only k1,k2   re-check only those entries; print their records
    python scripts/t1_bibliography.py --self-test   corrupt each record kind; require the check to reject it

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
CHECKED_ON_G7 = "2026-10-19"     # the fifteen entries added in round 5, G7 (the review's related work)
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
    # CHECKED_ON_S9. Until round 3 no fragment was recorded because §5.3 asserted nothing a paper SAYS
    # in prose (round 3's R2 added two for hafner2019, below): the settings taken from DreamerV2 (and the PlaNet settings deliberately not
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
            "which replaces PlaNet's free nats with KL balancing. Round 3 (R2, ruling V9): 5.3 also "
            "says that rule X1 did not try PlaNet's latent overshooting, what that objective trains, "
            "and that PlaNet's own final RSSM agent did not need it; the two fragments below are "
            "those assertions, matched verbatim against the paper's HTML.",
        "fragments": [
            "which trains all multi-step predictions in latent space",
            "our final agent using the RSSM model does not require it",
        ],
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
    # --- Round 5, G7: the works the TMLR review of 19 Oct 2026 names, and three the technical fixes cite. None is
    # cited in the text yet (G11-G15 add the sentences), so none carries a fragment: a fragment is added with the
    # sentence that attributes a claim to the work. "establishes" says why the work is listed, not what it proves.
    {
        "key": "venkatraman2015",
        "doi": "10.1609/aaai.v29i1.9590",
        "title": "Improving Multi-Step Prediction of Learned Time Series Models",
        "authors": ["Arun Venkatraman", "Martial Hebert", "J. Andrew Bagnell"],
        # The publisher's record (Crossref and the AAAI page alike) prints the third author as "J.. Bagnell"; the
        # paper's own first page reads "J. Andrew Bagnell". The display name is checked against the PDF and the
        # record's spelling against the record.
        "record_spelling": {"J. Andrew Bagnell": "J.. Bagnell"},
        "pdf_url": "https://ojs.aaai.org/index.php/AAAI/article/download/9590/9449",
        "venue": "AAAI 2015",
        "venue_record": "Proceedings of the AAAI Conference on Artificial Intelligence",
        "year": 2015,
        "establishes": "named by the TMLR review (RV32) as prior work on multi-step model training",
        "why_we_engage": "it sets the prior for the paper's autoregressive against teacher-forced comparison.",
        "fragments": [],
    },
    {
        "key": "bengio2015",
        "arxiv": "1506.03099",
        "url": "https://proceedings.neurips.cc/paper_files/paper/2015/hash/e995f98d56967d946471af29d7bf99f1-Abstract.html",
        "title": "Scheduled Sampling for Sequence Prediction with Recurrent Neural Networks",
        "authors": ["Samy Bengio", "Oriol Vinyals", "Navdeep Jaitly", "Noam Shazeer"],
        "venue": "NeurIPS 2015",
        "venue_record": "Advances in Neural Information Processing Systems",
        "year": 2015,
        "establishes": "named by the TMLR review (RV32) as prior work on multi-step model training",
        "why_we_engage": "it sets the prior for the paper's autoregressive against teacher-forced comparison.",
        "fragments": [],
    },
    {
        "key": "talvitie2017",
        "arxiv": "1612.06018",
        "doi": "10.1609/aaai.v31i1.10850",
        "title": "Self-Correcting Models for Model-Based Reinforcement Learning",
        "authors": ["Erik Talvitie"],
        "venue": "AAAI 2017",
        "venue_record": "Proceedings of the AAAI Conference on Artificial Intelligence",
        "year": 2017,
        "establishes": "named by the TMLR review (RV32) as prior work on multi-step model training",
        "why_we_engage": "it sets the prior for the paper's autoregressive against teacher-forced comparison.",
        "fragments": [],
    },
    {
        "key": "lambert2021",
        "arxiv": "2012.09156",
        "doi": "10.1109/cdc45484.2021.9683134",
        "title": "Learning Accurate Long-term Dynamics for Model-based Reinforcement Learning",
        "authors": ["Nathan O. Lambert", "Albert Wilcox", "Howard Zhang", "Kristofer S. J. Pister",
                    "Roberto Calandra"],
        "venue": "IEEE CDC 2021",
        "venue_record": "2021 60th IEEE Conference on Decision and Control (CDC)",
        "year": 2021,
        "establishes": "named by the TMLR review (RV32) as prior work on multi-step model training; the review "
                       "gives no title, and this is the 2021 Lambert et al. paper on long-term dynamics for "
                       "model-based RL that the G7 search found",
        "why_we_engage": "it sets the prior for the paper's autoregressive against teacher-forced comparison.",
        "fragments": [],
    },
    {
        "key": "angelopoulos2021",
        "arxiv": "2107.07511",
        "title": "A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification",
        "authors": ["Anastasios N. Angelopoulos", "Stephen Bates"],
        "venue": "arXiv:2107.07511",
        "year": 2021,
        "establishes": "named by the TMLR review (RV33) as prior work on conformal prediction",
        "why_we_engage": "the paper's per-horizon recalibration is to be framed against split conformal prediction.",
        "fragments": [],
    },
    {
        "key": "stankeviciute2021",
        "url": "https://proceedings.neurips.cc/paper_files/paper/2021/hash/312f1ba2a72318edaaa995a67835fad5-Abstract.html",
        "title": "Conformal Time-series Forecasting",
        "authors": ["Kamile Stankeviciute", "Ahmed M. Alaa", "Mihaela van der Schaar"],
        "venue": "NeurIPS 2021",
        "venue_record": "Advances in Neural Information Processing Systems",
        "year": 2021,
        "establishes": "named by the TMLR review (RV33) as prior work on conformal prediction",
        "why_we_engage": "the paper's per-horizon recalibration is to be framed against split conformal prediction.",
        "fragments": [],
    },
    {
        "key": "lindemann2023",
        "arxiv": "2210.10254",
        "doi": "10.1109/lra.2023.3292071",
        "title": "Safe Planning in Dynamic Environments using Conformal Prediction",
        "authors": ["Lars Lindemann", "Matthew Cleaveland", "Gihyun Shim", "George J. Pappas"],
        "venue": "IEEE RA-L 2023",
        "venue_record": "IEEE Robotics and Automation Letters",
        "year": 2023,
        "establishes": "named by the TMLR review (RV33) as prior work on conformal prediction",
        "why_we_engage": "the paper's per-horizon recalibration is to be framed against split conformal prediction.",
        "fragments": [],
    },
    {
        "key": "osband2016",
        "arxiv": "1602.04621",
        "url": "https://proceedings.neurips.cc/paper_files/paper/2016/hash/8d8818c8e140c64c743113f563cf750f-Abstract.html",
        "title": "Deep Exploration via Bootstrapped DQN",
        "authors": ["Ian Osband", "Charles Blundell", "Alexander Pritzel", "Benjamin Van Roy"],
        "venue": "NeurIPS 2016",
        "venue_record": "Advances in Neural Information Processing Systems",
        "year": 2016,
        "establishes": "named by the TMLR review (RV34) as a shared-torso RL ensemble",
        "why_we_engage": "the released ensemble shares a state trunk.",
        "fragments": [],
    },
    {
        "key": "osband2018",
        "arxiv": "1806.03335",
        "url": "https://proceedings.neurips.cc/paper_files/paper/2018/hash/5a7b238ba0f6502e5d6be14424b20ded-Abstract.html",
        "title": "Randomized Prior Functions for Deep Reinforcement Learning",
        "authors": ["Ian Osband", "John Aslanides", "Albin Cassirer"],
        "venue": "NeurIPS 2018",
        "venue_record": "Advances in Neural Information Processing Systems",
        "year": 2018,
        "establishes": "named by the TMLR review (RV34) as a shared-torso RL ensemble",
        "why_we_engage": "the released ensemble shares a state trunk.",
        "fragments": [],
    },
    {
        "key": "agarwal2021",
        "arxiv": "2108.13264",
        "url": "https://proceedings.neurips.cc/paper_files/paper/2021/hash/f514cec81cb148559cf475e7426eed5e-Abstract.html",
        "title": "Deep Reinforcement Learning at the Edge of the Statistical Precipice",
        "authors": ["Rishabh Agarwal", "Max Schwarzer", "Pablo Samuel Castro", "Aaron Courville",
                    "Marc G. Bellemare"],
        "venue": "NeurIPS 2021",
        "venue_record": "Advances in Neural Information Processing Systems",
        "year": 2021,
        "establishes": "named by the TMLR review (RV35) as prior work on RL evaluation statistics",
        "why_we_engage": "the paper's intervals rest on few seeds and few trajectories.",
        "fragments": [],
    },
    {
        "key": "henderson2018",
        "arxiv": "1709.06560",
        "doi": "10.1609/aaai.v32i1.11694",
        "title": "Deep Reinforcement Learning that Matters",
        "authors": ["Peter Henderson", "Riashat Islam", "Philip Bachman", "Joelle Pineau", "Doina Precup",
                    "David Meger"],
        "venue": "AAAI 2018",
        "venue_record": "Proceedings of the AAAI Conference on Artificial Intelligence",
        "year": 2018,
        "establishes": "named by the TMLR review (RV35) as prior work on RL evaluation statistics",
        "why_we_engage": "the paper's intervals rest on few seeds and few trajectories.",
        "fragments": [],
    },
    {
        "key": "cameron2008",
        "doi": "10.1162/rest.90.3.414",
        "title": "Bootstrap-Based Improvements for Inference with Clustered Errors",
        "authors": ["A. Colin Cameron", "Jonah B. Gelbach", "Douglas L. Miller"],
        "venue": "Review of Economics and Statistics 90(3)",
        "venue_record": "Review of Economics and Statistics",
        "year": 2008,
        "establishes": "cluster bootstraps when clusters are few; cited by the technical fixes for the "
                       "trajectory-clustered intervals",
        "why_we_engage": "the paper resamples whole trajectories, of which there are few.",
        "fragments": [],
    },
    {
        "key": "kingma2015",
        "arxiv": "1412.6980",
        "title": "Adam: A Method for Stochastic Optimization",
        "authors": ["Diederik P. Kingma", "Jimmy Ba"],
        "venue": "ICLR 2015",
        "venue_comment": "Published as a conference paper at the 3rd International Conference for Learning "
                         "Representations",
        "year": 2015,
        "establishes": "the Adam optimiser; cited by the technical fixes for the per-iteration step bound (N13)",
        "why_we_engage": "section 7.5's collapse argument is recast as Adam's step bound.",
        "fragments": [],
    },
    {
        "key": "prereg2020",
        "url": "https://proceedings.mlr.press/v148/",
        "editors": True,
        "title": "NeurIPS 2020 Workshop on Pre-registration in Machine Learning",
        "authors": ["Luca Bertinetto", "Jo\u00e3o F. Henriques", "Samuel Albanie", "Michela Paganini",
                    "G\u00fcl Varol"],
        "venue": "PMLR 148",
        "venue_record": "Published as Volume 148 by the Proceedings of Machine Learning Research",
        "year": 2021,
        "establishes": "named by the TMLR review (RV36) as a venue for pre-registration in ML; the workshop was held "
                       "in one year and its proceedings published the next",
        "why_we_engage": "the paper's decision rules are pre-registered in git before the data exist.",
        "fragments": [],
    },
    {
        "key": "prereg2021",
        "url": "https://proceedings.mlr.press/v181/",
        "editors": True,
        "title": "NeurIPS 2021 Workshop on Pre-registration in Machine Learning",
        "authors": ["Samuel Albanie", "Jo\u00e3o F. Henriques", "Luca Bertinetto", "Alex Hern\u00e1ndez-Garc\u00eda",
                    "Hazel Doughty", "G\u00fcl Varol"],
        "venue": "PMLR 181",
        "venue_record": "Published as Volume 181 by the Proceedings of Machine Learning Research",
        "year": 2022,
        "establishes": "named by the TMLR review (RV36) as a venue for pre-registration in ML; the workshop was held "
                       "in one year and its proceedings published the next",
        "why_we_engage": "the paper's decision rules are pre-registered in git before the data exist.",
        "fragments": [],
    },
]


# Round 5, G7: references 1 and 2, the papers reproduced. They are typed in the template, not generated, but every
# field the reference states is verified here: the title of the version we read (v1) and of the current version, from
# each version's arXiv abstract page; the current version's id, from the arXiv API, which must equal the one
# results/version_crosswalk.json records; and the workshop presentation, from the venue's own page, which must say
# "Poster in Workshop: <name>" beside the title and every author. Whether the page says anything about archival
# status is recorded, so "the page does not say" is checked rather than assumed.
ORIGINALS = [
    {
        "key": "li2025rwm",
        "family": "RWM",
        "arxiv": "2501.10100",
        "read": "v1",
        "authors": ["Chenhao Li", "Andreas Krause", "Marco Hutter"],
        "title_read": "Robotic World Model: A Neural Network Simulator for Robust Policy Optimization in Robotics",
        "title_current": "Robotic World Model: A Neural Network Simulator for Robust Policy Optimization in Robotics",
        "workshop_url": "https://neurips.cc/virtual/2025/123991",
        "workshop_label": "Poster in Workshop: Embodied World Models for Decision Making",
        "workshop_conference": "NeurIPS 2025",
    },
    {
        "key": "li2025rwmu",
        "family": "RWMU",
        "arxiv": "2504.16680",
        "read": "v1",
        "authors": ["Chenhao Li", "Andreas Krause", "Marco Hutter"],
        "title_read": "Offline Robotic World Model: Learning Robotic Policies without a Physics Simulator",
        "title_current": "Uncertainty-Aware Robotic World Model Makes Offline Model-Based Reinforcement Learning Work "
                         "on Real Robots",
        "workshop_url": "https://iclr.cc/virtual/2026/10018013",
        "workshop_label": "Poster in Workshop: The 2nd Workshop on World Models: Understanding, Modelling and Scaling",
        "workshop_conference": "ICLR 2026",
    },
]


def verify_originals():
    """Re-check every field of ORIGINALS against arXiv and the venue pages (needs the network)."""
    xw = json.load(open(os.path.join(R.RESULTS, "version_crosswalk.json")))["families"]
    root = ET.fromstring(fetch("https://export.arxiv.org/api/query?id_list="
                               + ",".join(o["arxiv"] for o in ORIGINALS)))
    latest = {e.find("a:id", ATOM).text.rsplit("/", 1)[-1].split("v")[0]:
              "v" + e.find("a:id", ATOM).text.rsplit("v", 1)[-1] for e in root.findall("a:entry", ATOM)}
    out = []
    for o in ORIGINALS:
        cur = latest.get(o["arxiv"])
        m_read = page_meta(fetch(f"https://arxiv.org/abs/{o['arxiv']}{o['read']}"))
        m_cur = page_meta(fetch(f"https://arxiv.org/abs/{o['arxiv']}{cur}"))
        folded = _fold(flatten(fetch(o["workshop_url"])))
        has = lambda x: _fold(x) in folded
        out.append({
            "key": o["key"],
            "current_version": cur,
            "current_matches_crosswalk": cur == xw[o["family"]]["current"],
            "read_title_matches": m_read["title"] == o["title_read"],
            "current_title_matches": m_cur["title"] == o["title_current"],
            "authors_match": m_read["authors"] == o["authors"] == m_cur["authors"],
            "workshop_label_found": has(o["workshop_label"]),
            "workshop_title_found": has(o["title_current"]),
            "workshop_authors_found": all(has(a) for a in o["authors"]),
            "workshop_conference_found": has(o["workshop_conference"]),
            "workshop_page_mentions_archival": "archival" in folded,
            "entry_fingerprint": originals_fingerprint(o),
        })
    return out


def originals_fingerprint(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]


_ORIGINALS_OK = ("current_matches_crosswalk", "read_title_matches", "current_title_matches", "authors_match",
                 "workshop_label_found", "workshop_title_found", "workshop_authors_found", "workshop_conference_found")


def flatten(raw):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw)))


def fetch(url, tries=3):
    """GET url. Round 5, G7: a timeout or a 429/5xx is retried twice after a pause; any other error is raised."""
    import time
    import urllib.error
    req = urllib.request.Request(url, headers={"User-Agent": "rwm-repro/1.0"})
    for k in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=60) as f:
                return f.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code != 429 and e.code < 500 or k == tries - 1:
                raise
        except (urllib.error.URLError, TimeoutError):
            if k == tries - 1:
                raise
        time.sleep(15 * (k + 1))


def _norm_name(s):
    import unicodedata
    # a dotless i (PMLR prints "Garc\u0131\u0301a") has no decomposition, so it is mapped by hand
    s = unicodedata.normalize("NFKD", s.replace("\u0131", "i"))
    return re.sub(r"[^a-z]", "", "".join(c for c in s if not unicodedata.combining(c)).lower())


def _fold(s):
    """Lower case, diacritics removed, whitespace collapsed: for finding a full name in a page's text."""
    import unicodedata
    s = unicodedata.normalize("NFKD", s.replace("\u0131", "i"))
    return re.sub(r"\s+", " ", "".join(c for c in s if not unicodedata.combining(c)).lower())


def crossref(doi):
    """Title, full author list, venue and year from the Crossref record of a DOI (round 5, G7)."""
    m = json.loads(fetch(f"https://api.crossref.org/works/{doi}"))["message"]
    authors = [" ".join(x for x in (a.get("given"), a.get("family")) if x) for a in m.get("author", [])]
    when = m.get("published-print") or m.get("published-online") or m.get("issued") or {}
    year = when.get("date-parts", [[None]])[0][0]
    return {"title": re.sub(r"\s+", " ", (m.get("title") or [""])[0]).strip(), "authors": authors,
            "venue": (m.get("container-title") or [""])[0], "year": year, "doi": doi}


def page_meta(raw):
    """The citation_* meta tags of a proceedings page (Highwire/Google Scholar convention), or None if it has none.
    Authors arrive as "Family, Given" and are returned as "Given Family", in page order."""
    tags = re.findall(r'<meta\s+name="citation_([a-z_]+)"\s+content="([^"]*)"', raw)
    if not any(k == "title" for k, _ in tags):
        return None
    one = lambda k: next((html.unescape(v) for t, v in tags if t == k), None)
    authors = [" ".join(reversed([x.strip() for x in html.unescape(v).split(",", 1)])) for t, v in tags
               if t == "author"]
    date = one("publication_date") or ""
    return {"title": one("title"), "authors": authors,
            "venue": one("journal_title") or one("conference_title"), "volume": one("volume"),
            "year": int(date[:4]) if date[:4].isdigit() else None}


def pdf_has(url, names):
    """True if every name appears, as whole words, in the first page of the PDF at url (whitespace collapsed, and
    also with spaces removed, since PDF text extraction splits some letter pairs)."""
    import io
    import pypdf
    req = urllib.request.Request(url, headers={"User-Agent": "rwm-repro/1.0"})
    with urllib.request.urlopen(req, timeout=60) as f:
        text = pypdf.PdfReader(io.BytesIO(f.read())).pages[0].extract_text()
    flat, tight = re.sub(r"\s+", " ", text), re.sub(r"\s+", "", text)
    whole = lambda n, t: re.search(r"(?<![A-Za-z])" + re.escape(n) + r"(?![A-Za-z])", t) is not None
    return all(whole(n, flat) or whole(n.replace(" ", ""), tight) for n in names)


def verify_record(ent):
    """Round 5, G7: an entry with no arXiv id is verified against its DOI's Crossref record or, with no DOI, against
    its proceedings page; an entry with an arXiv id and a DOI or page keeps arXiv as the source of its title and
    authors and has its venue and year checked there. On a page with citation_* meta tags, title, ordered author
    list, venue and year are read from the tags; a page without them (a volume's index) must contain the title,
    every author's full name (as whole words), the venue and the year as text."""
    norm = lambda x: re.sub(r"[^a-z0-9]", "", (x or "").lower())
    names = lambda xs: [_norm_name(a) for a in xs]
    rec = {}
    if ent.get("doi"):
        c = crossref(ent["doi"])
        rec.update({"record": "crossref", "doi": ent["doi"], "title_record": c["title"], "authors_record": c["authors"],
                    "venue_record": c["venue"], "year_record": c["year"]})
    elif ent.get("url"):
        raw = fetch(ent["url"])
        m = page_meta(raw)
        rec.update({"record": "page_meta" if m else "page_text", "url": ent["url"]})
        if m:
            rec.update({"title_record": m["title"], "authors_record": m["authors"], "venue_record": m["venue"],
                        "year_record": m["year"]})
        else:
            folded = _fold(flatten(raw))
            has = lambda x: re.search(r"(?<![a-z0-9])" + re.escape(_fold(str(x))) + r"(?![a-z0-9])", folded) is not None
            rec["venue_record"] = ent["venue_record"] if has(ent["venue_record"]) else None
            rec["year_record"] = ent["year"] if has(ent["year"]) else None
            rec["title_record"] = ent["title"] if has(ent["title"]) else None
            rec["authors_record"] = ent["authors"] if all(has(a) for a in ent["authors"]) else None
    rec["venue_matches"] = norm(rec.get("venue_record")) == norm(ent.get("venue_record")) != ""
    rec["year_matches"] = rec.get("year_record") == ent["year"]
    if not ent.get("arxiv"):
        spell = ent.get("record_spelling", {})
        rec["title_matches"] = norm(rec.get("title_record")) == norm(ent["title"])
        rec["authors_match"] = rec.get("authors_record") is not None and \
            names(rec["authors_record"]) == names([spell.get(a, a) for a in ent["authors"]])
        if spell:
            rec["record_spelling"] = spell
            rec["display_names_in_pdf"] = pdf_has(ent["pdf_url"], list(spell))
            rec["authors_match"] = rec["authors_match"] and rec["display_names_in_pdf"]
    if ent.get("fragments") and not ent.get("arxiv"):
        body = flatten(fetch(ent.get("fragment_source") or ent.get("url") or f"https://doi.org/{ent['doi']}"))
        rec["fragments"] = [{"fragment": f[:70], "found": re.sub(r"\s+", " ", f) in body} for f in ent["fragments"]]
        rec["n_fragments_found"] = sum(1 for f in rec["fragments"] if f["found"])
        rec["n_fragments"] = len(rec["fragments"])
    return rec


def verify(only=None):
    """Re-fetch metadata and re-check every recorded fragment. Returns the record. `only`: keys to verify (the rest
    are not fetched)."""
    todo = [e for e in ENTRIES if only is None or e["key"] in only]
    ids = ",".join(e["arxiv"] for e in todo if e.get("arxiv"))
    root = ET.fromstring(fetch(
        f"https://export.arxiv.org/api/query?id_list={ids}&max_results=60")) if ids else None
    meta = {}
    if root is None:
        root = ET.fromstring("<feed xmlns='http://www.w3.org/2005/Atom'/>")
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
    for ent in todo:
        if not ent.get("arxiv"):
            rec = {"key": ent["key"], "found": True, **verify_record(ent)}
            per.append(rec)
            continue
        m = meta.get(ent["arxiv"])
        rec = {"key": ent["key"], "arxiv": ent["arxiv"], "found": m is not None}
        if ent.get("doi") or ent.get("url"):
            rec.update(verify_record(ent))
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
            if ent.get("venue_comment"):
                rec["venue_matches"] = ent["venue_comment"] in (m["comment"] or "")
        if ent["fragments"] and m:
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
CHECKED_ON_FULL = "2026-10-09"   # round 3, R2: all eighteen entries re-verified live after two fragments
# were added to hafner2019 (ruling V9); every pinned field agreed except that entry's fingerprint and its
# new fragments. Before that, on 2026-09-25, all sixteen entries were re-verified against arXiv. They had been
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
        'entry_fingerprint': '4c583f97c5835982',
        'n_fragments': 2,
        'n_fragments_found': 2},
    {   'key': 'hafner2021',
        'title_matches': True,
        'authors_match': True,
        'published': '2020-10-05',
        'arxiv_version': '2010.02193v4',
        'comment': 'Published at ICLR 2021. Website: https://danijar.com/dreamerv2',
        'entry_fingerprint': '8b3f331043afe526'},
    # The fifteen entries added in round 5, G7, verified by the same verify() on CHECKED_ON_G7 with ENTRIES
    # restricted to them (--verify --only); the eighteen above were not re-fetched.
    {   'key': 'venkatraman2015',
        'title_matches': True,
        'authors_match': True,
        'record': 'crossref',
        'doi': '10.1609/aaai.v29i1.9590',
        'venue_matches': True,
        'year_matches': True,
        'venue_record': 'Proceedings of the AAAI Conference on Artificial Intelligence',
        'year_record': 2015,
        'record_spelling': {'J. Andrew Bagnell': 'J.. Bagnell'},
        'display_names_in_pdf': True,
        'entry_fingerprint': '9d6b61fcfbeb2e80'},
    {   'key': 'bengio2015',
        'title_matches': True,
        'authors_match': True,
        'record': 'page_meta',
        'url': 'https://proceedings.neurips.cc/paper_files/paper/2015/hash/e995f98d56967d946471af29d7bf99f1-Abstract.html',
        'venue_matches': True,
        'year_matches': True,
        'venue_record': 'Advances in Neural Information Processing Systems',
        'year_record': 2015,
        'published': '2015-06-09',
        'arxiv_version': '1506.03099v3',
        'comment': None,
        'entry_fingerprint': '85850a5a31cf909b'},
    {   'key': 'talvitie2017',
        'title_matches': True,
        'authors_match': True,
        'record': 'crossref',
        'doi': '10.1609/aaai.v31i1.10850',
        'venue_matches': True,
        'year_matches': True,
        'venue_record': 'Proceedings of the AAAI Conference on Artificial Intelligence',
        'year_record': 2017,
        'published': '2016-12-19',
        'arxiv_version': '1612.06018v2',
        'comment': 'Original paper appeared in Proceedings of the 31st AAAI Conference on Artificial Intelligence, '
                   '2017. This version incorporates the appendix into document (rather than as supplementary '
                   'material), corrects a minor error in Lemma 1, and fixes some type-os',
        'entry_fingerprint': 'b5dd087917c67521'},
    {   'key': 'lambert2021',
        'title_matches': True,
        'authors_match': True,
        'record': 'crossref',
        'doi': '10.1109/cdc45484.2021.9683134',
        'venue_matches': True,
        'year_matches': True,
        'venue_record': '2021 60th IEEE Conference on Decision and Control (CDC)',
        'year_record': 2021,
        'published': '2020-12-16',
        'arxiv_version': '2012.09156v2',
        'comment': '8 pages, +4 pages appendix',
        'entry_fingerprint': '460f0760b88261e1'},
    {   'key': 'angelopoulos2021',
        'title_matches': True,
        'authors_match': True,
        'published': '2021-07-15',
        'arxiv_version': '2107.07511v6',
        'comment': 'Blog and tutorial video at http://angelopoulos.ai/blog/posts/gentle-intro/ ; Code is available '
                   'at https://github.com/aangelopoulos/conformal-prediction',
        'entry_fingerprint': '5275ef41cc2dabeb'},
    {   'key': 'stankeviciute2021',
        'title_matches': True,
        'authors_match': True,
        'record': 'page_meta',
        'url': 'https://proceedings.neurips.cc/paper_files/paper/2021/hash/312f1ba2a72318edaaa995a67835fad5-Abstract.html',
        'venue_matches': True,
        'year_matches': True,
        'venue_record': 'Advances in Neural Information Processing Systems',
        'year_record': 2021,
        'entry_fingerprint': '0c25413176be3d0e'},
    {   'key': 'lindemann2023',
        'title_matches': True,
        'authors_match': True,
        'record': 'crossref',
        'doi': '10.1109/lra.2023.3292071',
        'venue_matches': True,
        'year_matches': True,
        'venue_record': 'IEEE Robotics and Automation Letters',
        'year_record': 2023,
        'published': '2022-10-19',
        'arxiv_version': '2210.10254v2',
        'comment': None,
        'entry_fingerprint': '89d0bda45afad3b5'},
    {   'key': 'osband2016',
        'title_matches': True,
        'authors_match': True,
        'record': 'page_meta',
        'url': 'https://proceedings.neurips.cc/paper_files/paper/2016/hash/8d8818c8e140c64c743113f563cf750f-Abstract.html',
        'venue_matches': True,
        'year_matches': True,
        'venue_record': 'Advances in Neural Information Processing Systems',
        'year_record': 2016,
        'published': '2016-02-15',
        'arxiv_version': '1602.04621v3',
        'comment': None,
        'entry_fingerprint': '2117c6b467d9479b'},
    {   'key': 'osband2018',
        'title_matches': True,
        'authors_match': True,
        'record': 'page_meta',
        'url': 'https://proceedings.neurips.cc/paper_files/paper/2018/hash/5a7b238ba0f6502e5d6be14424b20ded-Abstract.html',
        'venue_matches': True,
        'year_matches': True,
        'venue_record': 'Advances in Neural Information Processing Systems',
        'year_record': 2018,
        'published': '2018-06-08',
        'arxiv_version': '1806.03335v2',
        'comment': None,
        'entry_fingerprint': 'd3f3d6f96dba8902'},
    {   'key': 'agarwal2021',
        'title_matches': True,
        'authors_match': True,
        'record': 'page_meta',
        'url': 'https://proceedings.neurips.cc/paper_files/paper/2021/hash/f514cec81cb148559cf475e7426eed5e-Abstract.html',
        'venue_matches': True,
        'year_matches': True,
        'venue_record': 'Advances in Neural Information Processing Systems',
        'year_record': 2021,
        'published': '2021-08-30',
        'arxiv_version': '2108.13264v4',
        'comment': 'Outstanding Paper Award at NeurIPS 2021. Website: https://agarwl.github.io/rliable. 28 Pages, 33 '
                   'Figures',
        'entry_fingerprint': '895354d76138f780'},
    {   'key': 'henderson2018',
        'title_matches': True,
        'authors_match': True,
        'record': 'crossref',
        'doi': '10.1609/aaai.v32i1.11694',
        'venue_matches': True,
        'year_matches': True,
        'venue_record': 'Proceedings of the AAAI Conference on Artificial Intelligence',
        'year_record': 2018,
        'published': '2017-09-19',
        'arxiv_version': '1709.06560v3',
        'comment': 'Accepted to the Thirthy-Second AAAI Conference On Artificial Intelligence (AAAI), 2018',
        'entry_fingerprint': '90141ef5490de6f2'},
    {   'key': 'cameron2008',
        'title_matches': True,
        'authors_match': True,
        'record': 'crossref',
        'doi': '10.1162/rest.90.3.414',
        'venue_matches': True,
        'year_matches': True,
        'venue_record': 'Review of Economics and Statistics',
        'year_record': 2008,
        'entry_fingerprint': '3efa9ec8d633d205'},
    {   'key': 'kingma2015',
        'title_matches': True,
        'authors_match': True,
        'venue_matches': True,
        'published': '2014-12-22',
        'arxiv_version': '1412.6980v9',
        'comment': 'Published as a conference paper at the 3rd International Conference for Learning '
                   'Representations, San Diego, 2015',
        'entry_fingerprint': '90a670c26075cf04'},
    {   'key': 'prereg2020',
        'title_matches': True,
        'authors_match': True,
        'record': 'page_text',
        'url': 'https://proceedings.mlr.press/v148/',
        'venue_matches': True,
        'year_matches': True,
        'venue_record': 'Published as Volume 148 by the Proceedings of Machine Learning Research',
        'year_record': 2021,
        'entry_fingerprint': '2a8adb436d850fc4'},
    {   'key': 'prereg2021',
        'title_matches': True,
        'authors_match': True,
        'record': 'page_text',
        'url': 'https://proceedings.mlr.press/v181/',
        'venue_matches': True,
        'year_matches': True,
        'venue_record': 'Published as Volume 181 by the Proceedings of Machine Learning Research',
        'year_record': 2022,
        'entry_fingerprint': '599ac0db00c6c968'}]


# verify_originals() on CHECKED_ON_G7, pinned as _PER_ENTRY is.
_ORIGINALS_PINNED = [   {   'key': 'li2025rwm',
        'current_version': 'v5',
        'current_matches_crosswalk': True,
        'read_title_matches': True,
        'current_title_matches': True,
        'authors_match': True,
        'workshop_label_found': True,
        'workshop_title_found': True,
        'workshop_authors_found': True,
        'workshop_conference_found': True,
        'workshop_page_mentions_archival': False,
        'entry_fingerprint': '6ce48413f4ab574c'},
    {   'key': 'li2025rwmu',
        'current_version': 'v3',
        'current_matches_crosswalk': True,
        'read_title_matches': True,
        'current_title_matches': True,
        'authors_match': True,
        'workshop_label_found': True,
        'workshop_title_found': True,
        'workshop_authors_found': True,
        'workshop_conference_found': True,
        'workshop_page_mentions_archival': False,
        'entry_fingerprint': '3993c07b8e357d2d'}]


def check_originals_pinned():
    pinned = {q["key"]: q for q in _ORIGINALS_PINNED}
    bad = [o["key"] for o in ORIGINALS if o["key"] not in pinned
           or pinned[o["key"]]["entry_fingerprint"] != originals_fingerprint(o)
           or not all(pinned[o["key"]][k] for k in _ORIGINALS_OK)]
    assert not bad and len(pinned) == len(ORIGINALS), (
        f"references 1-2: {bad} unverified, edited since verification or failing; run --verify --only {','.join(bad)}")


def fingerprint(ent):
    """A short hash of everything in an entry that verification checks against arXiv.

    Pinned into each RECORDED record at verification time, so that an entry edited AFTER it was
    verified -- a changed title, author list, identifier or fragment -- is caught rather than
    silently reported as verified. D-34 asked for coverage of every key; a key check alone would
    still pass an edited title, so the fingerprint covers the verified CONTENT, not just the key.
    """
    d = {"arxiv": ent.get("arxiv"), "title": ent["title"], "authors": ent["authors"], "fragments": ent["fragments"]}
    # round 5 (G7): a key an entry does not have is left out, so every earlier entry hashes as it did
    for k in ("doi", "url", "venue_record", "venue_comment", "record_spelling", "pdf_url", "editors", "year"):
        if ent.get(k) and (k != "year" or ent.get("doi") or ent.get("url") or not ent.get("arxiv")):
            d[k] = ent[k]
    blob = json.dumps(d, sort_keys=True, ensure_ascii=False)
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
          "arXiv HTML rendering after tag-stripping and whitespace collapse. Round 5 (G7): an entry "
          "with no arXiv id takes title, full author list, venue and year from its DOI's Crossref record "
          "or, with no DOI, from its proceedings page's citation meta tags (or, on a volume page with "
          "none, the page text); an arXiv entry that also names a DOI or proceedings page has its venue "
          "and year checked there, and one that names a venue_comment has it matched in the arXiv comment")
RECORDED = record_from(_PER_ENTRY, CHECKED_ON_FULL)


def _caught(q):
    return not q.get("title_matches") or not q.get("authors_match") or q.get("venue_matches") is False \
        or q.get("year_matches") is False


def self_test():
    """Round 5, G7: corrupt one field of each kind of record and require --verify to reject it (needs the network).
    Works on copies; ENTRIES is restored before returning."""
    import copy
    saved = copy.deepcopy(ENTRIES)

    def bagnel(e):
        e["authors"][2] = "J. Andrew Bagnel"
        e["record_spelling"] = {"J. Andrew Bagnel": "J.. Bagnell"}
    plants = {   # key: (what is corrupted, how)
        "venkatraman2015": ("display name not in the PDF (a prefix of the true one)", bagnel),
        "stankeviciute2021": ("author order, proceedings meta tags", lambda e: e["authors"].reverse()),
        "osband2018": ("year, proceedings meta tags", lambda e: e.__setitem__("year", 2019)),
        "cameron2008": ("year, Crossref", lambda e: e.__setitem__("year", 2007)),
        "talvitie2017": ("venue, Crossref, arXiv entry", lambda e: e.__setitem__("venue_record", "Proceedings of ICML")),
        "kingma2015": ("venue, arXiv comment", lambda e: e.__setitem__("venue_comment", "Published at NeurIPS")),
        "prereg2020": ("truncated title, volume page", lambda e: e.__setitem__("title", e["title"][:-3])),
        "prereg2021": ("truncated editor name, volume page", lambda e: e["authors"].__setitem__(-1, "G\u00fcl Varo")),
    }
    o_saved = copy.deepcopy(ORIGINALS)
    try:
        ORIGINALS[1]["title_read"] = ORIGINALS[1]["title_current"]      # the defect the review found (RV10)
        ORIGINALS[0]["workshop_label"] = "Poster in Workshop: World Models"
        o_planted = {q["key"]: q for q in verify_originals()}
    finally:
        ORIGINALS[:] = o_saved
    o_clean = verify_originals()
    try:
        clean = verify(set(plants))
        by = {e["key"]: e for e in ENTRIES}
        for k, (_, f) in plants.items():
            f(by[k])
        planted = {q["key"]: q for q in verify(set(plants))}
    finally:
        ENTRIES[:] = saved
    ok = not any(_caught(q) for q in clean) and all(q[k] for q in o_clean for k in _ORIGINALS_OK)
    print(f"  uncorrupted: {'all pass' if ok else 'FAIL'}")
    for k, what in (("li2025rwmu", "reference 2: v1 paired with the later title (RV10)"),
                    ("li2025rwm", "reference 1: a workshop the venue page does not name")):
        c = not all(o_planted[k][f] for f in _ORIGINALS_OK)
        ok = ok and c
        print(f"  {k:<20} {what:<56} {'caught' if c else 'NOT CAUGHT'}")
    for k, (what, _) in plants.items():
        c = _caught(planted[k])
        ok = ok and c
        print(f"  {k:<20} {what:<56} {'caught' if c else 'NOT CAUGHT'}")
    print(f"  BIBLIOGRAPHY SELF-TEST: {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true",
                    help="re-fetch from arXiv and re-check every entry (needs network)")
    ap.add_argument("--only", default=None,
                    help="with --verify: comma-separated keys to verify; prints their pinned records for _PER_ENTRY "
                         "and writes nothing under results/")
    ap.add_argument("--self-test", action="store_true",
                    help="corrupt one field of each record kind and require verification to reject it (network)")
    args = ap.parse_args()
    if args.self_test:
        sys.exit(0 if self_test() else 1)

    record = RECORDED
    originals = _ORIGINALS_PINNED
    if not args.verify:
        check_pinned_covers_entries(RECORDED["per_entry"])
        check_originals_pinned()
    if args.verify:
        only = set(args.only.split(",")) if args.only else None
        okeys = {o["key"] for o in ORIGINALS}
        assert only is None or only <= {e["key"] for e in ENTRIES} | okeys, f"unknown keys {only}"
        if only is None or only & okeys:
            originals = [q for q in verify_originals() if only is None or q["key"] in only]
            obad = [q["key"] for q in originals if not all(q[k] for k in _ORIGINALS_OK)]
            assert not obad, f"references 1-2 fail verification: {obad}"
        if only is not None and not only - okeys:
            import pprint
            pprint.pprint(originals, indent=4, width=118, sort_dicts=False)
            print(f"  {len(originals)} of references 1-2 verified; nothing written")
            return
        per = verify(only - okeys if only else None)
        bad = [p for p in per if _caught(p)]
        frag_bad = [(p["key"], f["fragment"]) for p in per
                    for f in p.get("fragments", []) if not f["found"]]
        by_key = {e["key"]: e for e in ENTRIES}
        for q in per:
            q["entry_fingerprint"] = fingerprint(by_key[q["key"]])
        record = record_from(per, "RE-VERIFIED THIS RUN")
        assert not bad, f"metadata mismatch: {[b['key'] for b in bad]}"
        assert not frag_bad, f"fragments not found verbatim: {frag_bad}"
        if only:
            import pprint
            keep = ("key", "title_matches", "authors_match", "record", "doi", "url", "venue_matches", "year_matches",
                    "venue_record", "year_record", "record_spelling", "display_names_in_pdf", "published",
                    "arxiv_version", "comment", "n_fragments", "n_fragments_found", "entry_fingerprint")
            pprint.pprint([{k: q[k] for k in keep if k in q} for q in per], indent=4, width=118, sort_dicts=False)
            print(f"  {len(per)} entries verified; nothing written")
            return

    out = {
        "purpose": "every section 2 reference, verified against the paper itself",
        "rule": "no entry is added that was not verified. Title, full author list and "
                "venue come from the arXiv API, or for an entry with no arXiv id from its "
                "DOI's Crossref record or its proceedings page; anything our text asserts "
                "the paper SAYS is additionally matched verbatim against its HTML.",
        "evidence_class": "EXT",
        "entries": ENTRIES,
        "verification": record,
        "originals": ORIGINALS,
        "originals_verification": originals,
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
        ident = f"arXiv:{e['arxiv']}" if e.get("arxiv") else (f"doi:{e['doi']}" if e.get("doi") else e["url"])
        print(f"  [{mark}] {e['key']:<22} {e['venue']:<22} {ident}{frag}")
    print(f"\n  {record['n_metadata_verified']} of {len(ENTRIES)} entries "
          f"metadata-verified; {record.get('n_fragments_verbatim', 0)} of "
          f"{record.get('n_fragments_checked', 0)} asserted fragments verbatim")
    print(f"  references: {out['n_references_before']} -> {out['n_references_after']}")
    print(f"\n  wrote {R.rel(dst)}")


if __name__ == "__main__":
    main()
