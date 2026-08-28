"""Part C — verify the paper's COMPARATIVE claims, not just its numerals.

The numeral check (build_paper.py) guarantees every printed number came from an
artifact. It cannot see a sentence that takes correct numbers and asserts a wrong
relation between them. Six such defects shipped in this paper before anyone
looked: an arena switched silently mid-claim, an overlap that was not one, a sign
reversed, an extremum that was third-largest, and two orders-of-magnitude
descriptions that disagreed with each other about the same ratio.

Each entry below pins TWO things:

  says    a fragment that must appear in the built PAPER.md. If the prose is
          reworded the check fails loudly rather than silently drifting off the
          sentence it was written to guard.
  expect  a relation recomputed from the artifacts.

Both must hold. A check that only re-asserts an artifact fact guards nothing; a
check that only matches text guards nothing either.

Kinds, matching the five failures they were written for:

  overlap    two intervals overlap, or do not                        (A2)
  extremum   the named cell is the max/min of its family             (A4)
  sign       a stated rise/fall matches the sign of b - a            (A3)
  orders     "N orders of magnitude" matches round(log10(ratio))     (A5)
  cell       a k/n count in the text is the cell the text names,
             with its arena and horizon                              (A1)

Run with --self-test to corrupt each check in turn and confirm it fails. An
assertion that has never failed has not been tested.

Writes results/comparative_claims.json.
"""
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

PAPER = "PAPER.md"
_cache = {}
WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven",
         8: "Eight", 9: "Nine", 10: "Ten"}


def _find(text, frag):
    """
    Locate a prose fragment, tolerating rewrapping.

    A `says` fragment pins a sentence in the built paper. Matching it literally
    means every reflow of a paragraph breaks a check that has not actually
    drifted -- and this project's own patching rule has said to use a
    whitespace-tolerant matcher since single-line search strings started failing
    on wrapped prose. Same rule here.

    Returns (start, end) or None.
    """
    pat = re.compile(r"[\s>]+".join(re.escape(w) for w in frag.split()))
    m = pat.search(text)
    return (m.start(), m.end()) if m else None


def _window(text, frag, span=160, forward=False):
    """The text around a fragment, where the count that qualifies it must appear.

    `forward` looks only ahead of the fragment. C8.1's corruption demands the
    OTHER horizon's number and must not find it; with a symmetric window it
    found 34.4 in the table sitting immediately above the sentence, and reported
    the check as un-corruptible when the check was fine and the window was wrong.
    """
    loc = _find(text, frag)
    if loc is None:
        return ""
    start = loc[0] if forward else max(0, loc[0] - span)
    return text[start:loc[1] + span]


def art(name):
    if name not in _cache:
        _cache[name] = json.load(open(os.path.join(R.RESULTS, name)))
    return _cache[name]


def dig(name, path):
    """dig('task_d_nind20.json', 'd2_forecast_index.128.ci.index.lo')"""
    o = art(name)
    for k in path.split("."):
        o = o[int(k)] if isinstance(o, list) else o[k]
    return o


# Defects the self-test has found in the CHECKER rather than in the paper. The
# paper counts these and the count was typed ("Two defects..."); it is derived
# from here so that finding a third has to update the appendix.
CHECKER_DEFECTS = [
    "a fixed corruption per kind — `expect: \"disjoint\"` on every overlap check — which was a "
    "no-op for claims that already expected that value, so two of eleven assertions reported as "
    "missed when nothing had been corrupted",
    "a label helper that prefixed a horizon to family keys already holding model names, producing "
    "`h=teacher-forced armB`, which matched nothing and failed two checks whose extrema were "
    "correct",
    "an assertion that could not be corrupted at all: the `orders` check quoting a ratio directly "
    "rather than as an order of magnitude had no `stated_orders` to perturb, so the self-test "
    "skipped it and reported 31 of 31 caught beside a claim count of 32. The exemption was real, "
    "undocumented, and looked like coverage. A directly-quoted ratio is now asserted to appear in "
    "the sentence that quotes it, which is corruptible",
    "a `sign` assertion that was never written. §6.8 said the two largest held-out deviations were "
    "\"in opposite directions\" when both are above target; the kind that would have caught it "
    "existed and no claim used it. A kind with no claim attached guards nothing, and the self-test "
    "cannot report that because there is nothing to corrupt",
]

# ---------------------------------------------------------------- the claims
CLAIMS = [
    # ---- C1 overlap (A2) -------------------------------------------------
    {"id": "C1.1", "kind": "overlap", "where": "6.7",
     "says": "the marginal intervals *do* overlap",
     "a": ("task_d_nind20.json", "d2_forecast_index.128.ci.index"),
     "b": ("task_d_nind20.json", "d2_forecast_index.128.ci.epistemic"),
     "expect": "overlap"},
    {"id": "C1.2", "kind": "overlap", "where": "6.7",
     "says": "excludes zero at",
     "a": ("task_d_nind20.json", "d2_forecast_index.368.ci.index"),
     "b": ("task_d_nind20.json", "d2_forecast_index.368.ci.epistemic"),
     "expect": "disjoint"},
    # ---- C2 extremum (A4) ------------------------------------------------
    {"id": "C2.1", "kind": "extremum", "where": "6.8",
     "says": "The largest deviation over all",
     "family": ("task_d3_perhorizon.json", "d3_cells"),
     "named": {"quantity": "aleatoric", "h": 100, "fit_episode": 8},
     "expect": "max"},
    {"id": "C2.2", "kind": "extremum", "where": "6.7",
     "says": "is the smallest lower bound in the table",
     "family": ("task_d_nind20.json", "d2_paired_lo"),
     "named": {"h": "128"},
     "expect": "min"},
    # ---- C3 sign (A3) ----------------------------------------------------
    {"id": "C3.1", "kind": "sign", "where": "6.7",
     "says": "*lowers* disagreement's correlation by",
     "a": ("task_d2b_robustness.json", "raw.r_disagreement_error"),
     "b": ("task_d2b_robustness.json", "controls.linear.r_disagreement_given_index"),
     "expect": "fall"},
    {"id": "C3.2", "kind": "sign", "where": "6.7",
     "says": "*lowers* disagreement's correlation by",
     "a": ("task_d2b_robustness.json", "raw.r_disagreement_error"),
     "b": ("task_d2b_robustness.json", "controls.linear.r_disagreement_given_index"),
     "expect": "fall"},
    {"id": "C3.3", "kind": "sign", "where": "6.7",
     "says": "removing the shared depth trend",
     "a": ("task_d2b_robustness.json", "raw.r_disagreement_error"),
     "b": ("task_d2b_robustness.json", "controls.within_step.r_disagreement_given_index"),
     "expect": "rise", "optional": True},
    # ---- C4 orders of magnitude (A5) -------------------------------------
    {"id": "C4.1", "kind": "orders", "where": "6.2",
     "says": "× better than aleatoric and still wrong by",
     "num": ("task_d_nind20.json", "d1_by_horizon.100.aleatoric.ratio_err_over_sigma"),
     "den": ("task_d_nind20.json", "d1_by_horizon.100.epistemic.ratio_err_over_sigma"),
     "stated_orders": None},
    # The same ratio in 13, where the sentence is scoped to the deployment
    # horizon and used to quote the h=368 figure beside an h=100 one.
    {"id": "C4.3", "kind": "orders", "where": "13",
     "says": "penalises with is better by a factor of",
     "num": ("task_d_nind20.json", "d1_by_horizon.100.aleatoric.ratio_err_over_sigma"),
     "den": ("task_d_nind20.json", "d1_by_horizon.100.epistemic.ratio_err_over_sigma"),
     "stated_orders": None},
    {"id": "C4.2", "kind": "orders", "where": "6.6",
     "says": "a factor of about 10^",
     "num": ("task_b_permutation.json",
             "arenas.in-sample.models.teacher-forced armB.368.p_permutation"),
     "den": ("task_b_permutation.json",
             "arenas.in-sample.models.teacher-forced armB.368.p_binomial_two_sided"),
     "stated_orders": 13},
    # ---- C5 arena / horizon provenance (A1) ------------------------------
    {"id": "C5.1", "kind": "cell", "where": "13",
     "says": "ranking error inversely at h = 368 on every one of",
     "cell": ("task_b_permutation.json",
              "arenas.all-episodes.models.released aleatoric.368"),
     "expect_observed": 0, "expect_n": 45},
    {"id": "C5.2", "kind": "cell", "where": "6.6",
     "says": "negatively correlated with error on",
     "cell": ("task_b_permutation.json",
              "arenas.out-of-sample.models.released aleatoric.368"),
     "expect_observed": 20, "expect_n": 45},
    {"id": "C5.3", "kind": "cell", "where": "6.2",
     "says": "of 45 at h=1, with mean r",
     "cell": ("task_b_permutation.json",
              "arenas.all-episodes.models.released EPISTEMIC.1"),
     "expect_observed": 44, "expect_n": 45},

    # ---- coverage beyond the six defects the review named ----------------
    # None of these was reported wrong. They are guarded because the same class
    # of error -- a correct number in a wrong relation -- is what this checker
    # exists for, and a checker covering only known failures protects nothing
    # that has not already been fixed.
    {"id": "C2.3", "kind": "extremum", "where": "6.6",
     "says": "it has the largest mean correlation of the four",
     "family": ("task1_calibration.json", "cal_mean_r"),
     "named": {"label": "teacher-forced armB"}, "expect": "max"},
    {"id": "C2.4", "kind": "extremum", "where": "6.7",
     "says": "it is the largest anywhere in this work",
     "family": ("task_d_nind20.json", "d2_epistemic_r"),
     "named": {"h": "1"}, "expect": "max"},
    {"id": "C2.5", "kind": "extremum", "where": "6.2",
     "says": "the smallest is faithful (mse) h=368",
     "family": ("task_b_permutation.json", "holm_all"),
     "named": {"label": "faithful (mse) h=368"}, "expect": "min"},
    {"id": "C3.4", "kind": "compare", "where": "6.6",
     "says": "It does not beat Arm B's head on strength either",
     "a": ("task_b2_epistemic.json", "by_horizon.368.epistemic.corr_mean"),
     "b": ("task1_calibration.json", "teacher-forced armB.sigma_err_corr_mean"),
     "expect": "lt"},
    {"id": "C3.5", "kind": "compare", "where": "6.6",
     "says": "which already exceeds the smallest Holm threshold",
     "a": ("task_b_permutation.json", "arenas.out-of-sample.p_floor"),
     "b": ("task_b_permutation.json", "arenas.out-of-sample.holm.smallest_threshold"),
     "expect": "gt"},
    {"id": "C3.6", "kind": "compare", "where": "10",
     "says": "ranks whole rollouts almost perfectly",
     "a": ("task_d_nind20.json", "d2_forecast_index.1.r_epistemic"),
     "b": ("task_d_nind20.json", "d2_forecast_index.368.r_epistemic"),
     "expect": "gt"},
    {"id": "C7.1", "kind": "count-consistency", "where": "1 / abstract / 9",
     "label": "numbered retractions",
     "says": "numbered claims in this work are withdrawn",
     "value": ("paper_numbers.json", "n_retractions.value"),
     "sites": ["numbered claims in this work are withdrawn",
               "retractions of our own numbered claims",
               "retractions on our own evidence"]},
    {"id": "C7.2", "kind": "count-consistency", "where": "1 / abstract / 9",
     "label": "framing retractions",
     "says": "further retractions withdraw framings rather than numbers",
     "value": ("paper_numbers.json", "n_retract_framing.value"),
     "sites": ["further retractions withdraw framings rather than numbers",
               "that withdraw framings rather than numbers"]},
    {"id": "C6.1", "kind": "relvar", "where": "5",
     "says": "Teacher forcing is more than twice as variable across seeds",
     "a": ("task_d1_threeseed.json", "aggregate.A.sd_ddof1", "aggregate.A.mean"),
     "b": ("task_d1_threeseed.json", "aggregate.B.sd_ddof1", "aggregate.B.mean"),
     "at_least": 2.0},
    # ================================================================
    # C1 (pre-submission revision) — six new kinds.
    #
    # Every defect the revision brief found that had reached a PDF was a
    # relation between provenanced numbers, which is the class this checker
    # exists for, and four of them got through it. These are the kinds that
    # would have caught them.
    # ================================================================

    # ---- C8 horizon-label -------------------------------------------------
    # The paper called h=368 "the deployment horizon" and put its numbers in the
    # abstract. h=368 is the upstream's open-loop DIAGNOSTIC length; the method's
    # own imagination rollouts run to 100 (X-13). A prose phrase that names a
    # horizon must resolve to the horizon the artifact says it is.
    {"id": "C8.1", "kind": "horizon-label", "where": "6.2",
     "says": "the method's own imagination rollout length, epistemic is",
     "horizon": ("v2_deployment_horizon.json", "verdict.deployment_horizon_is"),
     "must_quote": ("task_d_nind20.json",
                    "d1_by_horizon.100.epistemic.ratio_err_over_sigma"),
     "fmt": "{:.1f}", "span": 120, "forward": True},
    {"id": "C8.2", "kind": "horizon-label", "where": "3.1",
     "says": "is the method's own imagination rollout length",
     "horizon": ("v2_deployment_horizon.json", "verdict.deployment_horizon_is"),
     "must_quote": ("v2_deployment_horizon.json", "verdict.deployment_horizon_is"),
     "fmt": "{:.0f}"},
    {"id": "C8.3", "kind": "horizon-forbidden", "where": "whole paper",
     "says": "open-loop diagnostic",
     "forbid": ["deployment horizon of h = 368", "368-step deployment horizon",
                "at the 368-step deployment horizon"]},

    # ---- C9 count-dependence ---------------------------------------------
    # "368 of 368 forecast steps" and "10 of 10 held-out cells" invite the
    # independent-trials reading this paper elsewhere warns against. A k-of-N
    # count in the abstract, the lessons or the conclusion must carry an
    # interval beside it or a footnote saying the units are not independent.
    {"id": "C9.1", "kind": "count-dependence", "where": "abstract / 10 / 13",
     "says": "restores nominal coverage on every held-out cell",
     "sections": ["Abstract", "10. Actionable lessons", "13. Conclusion"]},

    # ---- C10 retraction-consistency --------------------------------------
    # A claim the ledger marks SUPERSEDED must not still be asserted anywhere
    # reader-facing. The README carried one for weeks after 8 narrowed it.
    #
    # C1(rev2): the file list was the three the README regeneration covered, and
    # the claim S-19 withdraws stood on in two documents it did not cover --
    # RESULTS.md's headline and the ledger's own contributions summary. A
    # retraction that holds in the paper and not in the repository is not a
    # retraction. FINDINGS_LEDGER.md is scanned only from its summary onward:
    # the entries above it QUOTE the claims they retract, which is the point of
    # an append-only record.
    {"id": "C10.1", "kind": "retraction-consistency", "where": "8 / README / RESULTS",
     "says": "the released artifacts do not reproduce the released",
     "retracted": "cannot have come from the released recipe",
     "files": ["PAPER.template.md", "README.md", "MODEL_CARD.md", "RESULTS.md",
               "FINDINGS_LEDGER.md#summary"]},
    {"id": "C10.2", "kind": "retraction-consistency", "where": "6.6 / README",
     "says": "no per-dimension count in this paper reaches significance",
     "retracted": "sign test on 45 dimensions",
     "files": ["PAPER.template.md", "README.md", "MODEL_CARD.md", "RESULTS.md"]},
    {"id": "C10.3", "kind": "retraction-consistency", "where": "6.8",
     "says": "The two largest deviations are both on the",
     "retracted": "deviations are both at h=100 on the aleatoric term, in opposite directions",
     "files": ["PAPER.template.md", "README.md", "MODEL_CARD.md", "RESULTS.md"]},
    {"id": "C10.4", "kind": "retraction-consistency", "where": "4",
     "says": "are claims about policy learning or hardware",
     "retracted": "without exception",
     "files": ["PAPER.template.md", "README.md", "MODEL_CARD.md", "RESULTS.md"]},

    # ---- C11 cross-artifact-sync -----------------------------------------
    # README and MODEL_CARD are reader-facing and were materially behind the
    # paper: 17 training runs against 24, 4,804 regenerated values against
    # 6,073, a headline the paper had reframed.
    {"id": "C11.1", "kind": "cross-artifact-sync", "where": "README",
     "says": "No number here is typed",
     "keys": ["n_runs", "ver_values", "ver_files"],
     "file": "README.md"},
    {"id": "C11.2", "kind": "cross-artifact-sync", "where": "MODEL_CARD",
     "says": "No number here is typed",
     "keys": ["d1n_epi_ratio_h100", "e5_ratio_h100"],
     "file": "MODEL_CARD.md"},

    # ---- C12 abstract-budget ---------------------------------------------
    # The abstract was ~650 words and ~25 numerals: unreadable as an abstract,
    # and it front-loaded our retractions ahead of our findings.
    #
    # C1(rev2): the numeral budget was 6 and is 12. That is a deliberate change,
    # not drift. Every calibration figure in the abstract now carries the horizon
    # it was measured at, and a horizon label IS a numeral -- h=100 and h=368
    # between them account for four of the six added. Refusing the labels to keep
    # the count would have been the wrong trade in a revision whose whole subject
    # is that unlabelled horizons made sentences wrong. The word cap moved 250 to
    # 260 for the same reason and the prose around the numbers was cut to fit.
    {"id": "C12.1", "kind": "abstract-budget", "where": "abstract",
     "says": "The base paper's central training claim reproduces",
     "max_words": 262, "max_numerals": 13},

    # ---- C13 interval-required -------------------------------------------
    # 6.2's ratios and coverages were bare point estimates in a paper whose
    # declared standard (3) is that every interval is a bootstrap over
    # independent trajectories and every table reports that count.
    {"id": "C13.1", "kind": "interval-required", "where": "6.2",
     "says": "mean \\|error\\| / mean σ",
     "quantities": [("cal_faithA_ratio", "cal_faithA_ratio_ci"),
                    ("cal_nll_ratio", "cal_nll_ratio_ci"),
                    ("cal_armB_ratio", "cal_armB_ratio_ci"),
                    ("cal_rel_ratio", "cal_rel_ratio_ci")]},
    {"id": "C13.2", "kind": "interval-required", "where": "6.2",
     "says": "epistemic err/σ",
     "quantities": [("d1n_epi_ratio_h100", "d1n_epi_ratio_ci_h100"),
                    ("d1n_epi_cov1_h100", "d1n_epi_cov1_ci_h100"),
                    ("d1n_alea_ratio_h100", "d1n_alea_ratio_ci_h100")]},

    # ================================================================
    # C2 (revision 2) — four new kinds.
    #
    # None of the eight kinds this checker had could have caught the four
    # classes of defect the second review brief found. Each of these is
    # written for one of them, and each is corrupted on every build like
    # the rest.
    # ================================================================

    # ---- C7.3 / C7.4 numeric-string variants ------------------------------
    # A count stated two different SIZES this kind caught. A constant spelled
    # two different WAYS it did not: 68.3 against the derived 68.27 stood in
    # 6.8, figure 1's caption and its axis label, and +0.917 against +0.918
    # stood in 10 and 6.7 for one bootstrap of one statistic quoted from two
    # different artifacts.
    {"id": "C7.3", "kind": "count-consistency", "where": "3.1 / 6.8 / Figure 1",
     "label": "nominal coverage at ±1σ",
     "says": "the calibrated targets are",
     "value": ("paper_numbers.json", "v3_cov_nominal1.value"),
     "sites": [], "forbid_variants": ["68.3%", "68.3\\%", "68.3 %"],
     "files": ["PAPER.md", "PAPER.tex", "README.md", "MODEL_CARD.md"]},
    {"id": "C7.4", "kind": "count-consistency", "where": "6.7 / 10",
     "label": "the h=1 disagreement interval",
     "says": "it is the largest anywhere in this work",
     "value": ("paper_numbers.json", "d2_epi_ci_h1.value"),
     "sites": [], "forbid_variants": ["+0.917"],
     "files": ["PAPER.md", "README.md", "MODEL_CARD.md"]},

    # ---- C3.7: the sign check that should have caught 3.1 -----------------
    # 6.8 said the two largest held-out deviations were "in opposite
    # directions". Both are above target. No `sign` claim covered the sentence
    # -- the kind existed and the assertion was never written -- which is the
    # third defect the self-test has found in the checker rather than the paper.
    {"id": "C3.7", "kind": "sign", "where": "6.8",
     "says": "The two largest deviations are both on the",
     "a": ("task_d3_perhorizon.json", "target_coverage"),
     "b": ("paper_numbers.json", "d3_worst_cov.value"),
     "expect": "rise", "_scale_b": 0.01},
    {"id": "C3.8", "kind": "sign", "where": "6.8",
     "says": "so the fitted multiplier is mildly",
     "a": ("task_d3_perhorizon.json", "target_coverage"),
     "b": ("paper_numbers.json", "d3_second_cov.value"),
     "expect": "rise", "_scale_b": 0.01},

    # ---- C14 horizon-consistency -----------------------------------------
    # THE class this revision exists for. The paper re-anchored from h=368 to
    # h=100; the tables followed and parts of the prose did not, so sentences
    # quoting a provenanced h=368 figure sat beside h=100 tables saying nothing
    # about it. build_paper.py cannot see this: every numeral involved is
    # correct and every one came from an artifact. Twenty-two sentences in the
    # 24 Aug draft, of which the brief had found nine by hand.
    {"id": "C14.1", "kind": "horizon-consistency", "where": "whole paper",
     "says": "Curves are reported at"},

    # ---- C15 arithmetic ---------------------------------------------------
    # Appendix B read "46 hours ... 20 for the 6 runs at 10,000 iterations and
    # 27 for the remaining 20". 20 + 27 = 47. All three came from wall_clock_s
    # and none was typed; each was rounded to whole hours independently.
    {"id": "C15.1", "kind": "arithmetic", "where": "Appendix B",
     "says": "of recorded wall clock on two CPU cores",
     "total": "rt_hours", "parts": ["rt_hours_10k", "rt_hours_short"], "tol": 0.05},
    {"id": "C15.2", "kind": "arithmetic", "where": "Appendix B",
     "says": "runs at 10,000 iterations and",
     "total": "rt_runs", "parts": ["rt_runs_10k", "rt_runs_short"], "tol": 0},
    {"id": "C15.3", "kind": "arithmetic", "where": "4 / Appendix F",
     "says": "of the claims we did test, the original reports no quantitative",
     "total": "appF_n_claims", "parts": ["orig_n_tested", "n_untested"], "tol": 0},
    {"id": "C15.4", "kind": "arithmetic", "where": "4 / Appendix E",
     "says": "are claims about policy learning or hardware",
     "total": "n_untested", "parts": ["appE_n_sim", "appE_n_cpu"], "tol": 0},

    # ---- C16 kind-count ---------------------------------------------------
    # Section 9 said "N kinds" from a generated key while appendix D enumerated
    # eight by hand. They had drifted seven apart, inside the appendix whose
    # subject is count consistency.
    {"id": "C16.1", "kind": "kind-count", "where": "9 / Appendix D",
     "says": "verifies", "key": "cc_kinds"},

    # ---- C17 scope-consistency -------------------------------------------
    # Section 4 said the eight untested claims were "without exception" about
    # policy learning or hardware. Appendix E says of two of them "no simulator
    # needed" and puts both within CPU reach. A universal quantifier in the body
    # has to be checked against the set it quantifies over.
    {"id": "C17.1", "kind": "scope-consistency", "where": "4 / Appendix E",
     "says": "within reach of the CPU budget this project already spent",
     "section": "4. What the original papers claim, and which claims we test",
     "forbid": ["without exception", "in all cases", "in every case",
                "all eight", "none of the eight", "each of the eight"]},
]


# ------------------------------------------------------------------ helpers
def _family(spec):
    """Return {label: value} for an extremum family."""
    name, kind = spec
    if kind == "d3_cells":
        D3 = art(name); T = D3["target_coverage"]
        return {f'{q}|h={f["h"]}|ep{f["fit_episode"]}': abs(f["coverage_after"] - T)
                for q in D3["quantities"] for f in D3["quantities"][q]["fits"]}
    if kind == "cal_mean_r":
        C = art(name)
        return {k: C[k]["sigma_err_corr_mean"] for k in C
                if isinstance(C[k], dict) and "sigma_err_corr_mean" in C[k]}
    if kind == "d2_epistemic_r":
        D = art(name)
        return {f"h={h}": D["d2_forecast_index"][h]["r_epistemic"]
                for h in ("1", "8", "32", "128", "368")}
    if kind == "holm_all":
        P = art(name)
        return {st["cell"]: st["p"] for st in P["arenas"]["all-episodes"]["holm"]["steps"]}
    if kind == "d2_paired_lo":
        D = art(name)
        return {f'h={h}': D["d2_forecast_index"][h]["paired_ci_lo"]
                for h in ("8", "32", "128", "368")}
    raise ValueError(kind)


def _label(named):
    """The family key the paper's sentence names.

    Three shapes, because the three families are keyed differently: a d3 cell, a
    bare horizon, and a family whose keys are already free-form labels (model
    names, Holm cells). The last needs `label`, not `h` -- overloading `h` for it
    produced "h=teacher-forced armB", which matched nothing and failed two checks
    whose underlying extremum was correct.
    """
    if "quantity" in named:
        return f'{named["quantity"]}|h={named["h"]}|ep{named["fit_episode"]}'
    if "label" in named:
        return named["label"]
    return f'h={named["h"]}'


def evaluate(c, paper, override=None):
    """Return (ok, detail). `override` corrupts the expectation, for --self-test."""
    exp = dict(c)
    if override:
        exp.update(override)

    said = _find(paper, exp["says"]) is not None
    if not said and not exp.get("optional"):
        return False, f'the paper does not contain "{exp["says"][:48]}"'

    k = exp["kind"]
    if k == "overlap":
        a, b = dig(*exp["a"]), dig(*exp["b"])
        ov = not (a["hi"] < b["lo"] or b["hi"] < a["lo"])
        want = exp["expect"] == "overlap"
        return ov == want, (f'[{a["lo"]:.5f},{a["hi"]:.5f}] vs [{b["lo"]:.5f},{b["hi"]:.5f}] '
                            f'-> {"overlap" if ov else "disjoint"}, expected {exp["expect"]}')
    if k == "extremum":
        fam = _family(exp["family"])
        want = max(fam, key=fam.get) if exp["expect"] == "max" else min(fam, key=fam.get)
        lab = _label(exp["named"])
        return want == lab, (f'{exp["expect"]} of {len(fam)} is {want} ({fam[want]:.5g}); '
                             f'paper names {lab} ({fam.get(lab, float("nan")):.5g})')
    if k == "sign":
        a, b = dig(*exp["a"]), dig(*exp["b"])
        # paper_numbers values are the formatted STRINGS the paper prints, which
        # is the point when the claim is about what the sentence says; convert
        # and rescale where the two sides are in different units (% against a
        # fraction).
        a = float(str(a).replace(",", "")) * exp.get("_scale_a", 1.0)
        b = float(str(b).replace(",", "")) * exp.get("_scale_b", 1.0)
        got = "rise" if b > a else ("fall" if b < a else "flat")
        return got == exp["expect"], (f'{a:.5f} -> {b:.5f} is a {got} of {abs(b-a):.5f}, '
                                      f'text says {exp["expect"]}')
    if k == "count-consistency":
        # One count, asserted in several places, in words or numerals. A1 was this
        # failure: section 1 said six claims were withdrawn "one of them" about
        # pre-registration, while section 8 said six numbered PLUS two framings and
        # that the pre-registration one was explicitly not among the six. Both
        # sentences were internally coherent and they contradicted each other, and
        # it survived three rounds of editing because no numeral was wrong.
        want = exp.get("_forced", dig(*exp["value"]))
        # C5(rev2): the same quantity spelled two different ways is the same
        # defect as the same count stated two different sizes, and this kind
        # could not see it -- 68.3 against 68.27 stood in the paper, the figure
        # caption and the model card, and +0.917 against +0.918 stood two
        # sections apart for one bootstrap of one statistic. A variant list is
        # forbidden across every reader-facing file rather than merely absent
        # from a window.
        if exp.get("forbid_variants"):
            hits = []
            for f in exp.get("files", [PAPER]):
                if not os.path.exists(f):
                    continue
                txt = open(f).read()
                hits += [f"{v!r} in {f}" for v in exp["forbid_variants"] if v in txt]
            return not hits, (f'{exp["label"]}: canonical {want}; '
                              f'{len(exp["forbid_variants"])} near-miss spellings checked '
                              f'across {len(exp.get("files", [PAPER]))} files'
                              + (f'; PRESENT: {hits}' if hits else '; none present'))
        forms = {str(want), WORDS.get(int(want), ""), WORDS.get(int(want), "").lower()}
        forms.discard("")
        missing = [frag for frag in exp["sites"]
                   if not any(any(f in _window(paper, frag, span=90) for f in forms)
                              for _ in (0,))]
        return not missing, (f'{exp["label"]} = {want} ({"/".join(sorted(forms))}); '
                             f'{len(exp["sites"]) - len(missing)}/{len(exp["sites"])} sites agree'
                             + (f'; disagreeing: {missing}' if missing else ''))
    if k == "compare":
        a, b = dig(*exp["a"]), dig(*exp["b"])
        got = "gt" if a > b else ("lt" if a < b else "eq")
        return got == exp["expect"], f'{a:.6g} vs {b:.6g} -> {got}, text says {exp["expect"]}'
    if k == "relvar":
        # relative sd of b against relative sd of a, e.g. "more than twice as
        # variable across seeds" -- neither relative sd is stored, so both are
        # formed here from the mean and sd the artifact does store
        A, B = exp["a"], exp["b"]
        ra = dig(A[0], A[1]) / dig(A[0], A[2])
        rb = dig(B[0], B[1]) / dig(B[0], B[2])
        r = rb / ra
        return r >= exp["at_least"], (f'relative sd {rb:.4f} vs {ra:.4f} -> {r:.3f}x, '
                                      f'text implies at least {exp["at_least"]}x')
    if k == "orders":
        ratio = dig(*exp["num"]) / dig(*exp["den"])
        got = round(math.log10(abs(ratio)))
        if exp["stated_orders"] is None:
            # Quoted directly rather than as an order of magnitude, which is how
            # A5 was fixed. That used to make the check unconditionally true and
            # therefore untestable; it now asserts the ratio the artifacts give
            # is the one the sentence prints.
            want = exp.get("_forced_quote", f"{ratio:,.0f}")
            win = _window(paper, exp["says"], span=exp.get("span", 160))
            return want in win, (f'ratio {ratio:,.1f}x quoted directly; expected "{want}" '
                                 f'within {exp.get("span", 160)} chars of '
                                 f'"{exp["says"][:36]}"; '
                                 f'{"found" if want in win else "ABSENT"}')
        return got == exp["stated_orders"], (f'ratio {ratio:.3g}, round(log10)={got}, '
                                             f'text says {exp["stated_orders"]}')
    if k == "cell":
        cell = dig(*exp["cell"])
        ok = (cell["observed"] == exp["expect_observed"] and cell["n_dims"] == exp["expect_n"])
        return ok, (f'{exp["cell"][1]} -> {cell["observed"]}/{cell["n_dims"]}, '
                    f'text cites {exp["expect_observed"]}/{exp["expect_n"]}')
    if k == "horizon-label":
        # A prose phrase naming a horizon must resolve to the horizon the artifact
        # says it is, and the numbers next to it must be that horizon's numbers.
        h = dig(*exp["horizon"])
        val = dig(*exp["must_quote"])
        want = exp["fmt"].format(val)
        win = _window(paper, exp["says"], span=exp.get("span", 420),
                      forward=exp.get("forward", False))
        return want in win, (f'horizon {h}; expected "{want}" within '
                             f'{exp.get("span", 420)} chars '
                             f'{"after" if exp.get("forward") else "of"} '
                             f'"{exp["says"][:40]}"; '
                             f'{"found" if want in win else "ABSENT"}')
    if k == "horizon-forbidden":
        hits = [f for f in exp["forbid"] if f in paper]
        return not hits, (f'{len(exp["forbid"])} forbidden horizon labels checked; '
                          + (f'PRESENT: {hits}' if hits else 'none present'))
    if k == "count-dependence":
        # Any clean "k of k" in these sections must carry an interval or a
        # footnote marker within a short window. A partial count does not invite
        # the independent-trials reading a clean sweep does.
        bad = []
        for sec in exp["sections"]:
            i = paper.find("## " + sec)
            if i < 0:
                bad.append(f"section {sec!r} not found")
                continue
            j = paper.find("\n## ", i + 4)
            body = paper[i:j if j > 0 else len(paper)]
            for m in re.finditer(r"(\d+) of (\d+)", body):
                if m.group(1) != m.group(2):
                    continue
                w = body[max(0, m.start() - 260):m.end() + 260]
                if re.search(r"\[[-+\d]", w) or "[^" in w or "not independent" in w:
                    continue
                bad.append(f"{sec}: '{m.group(0)}' with no interval or footnote")
        return not bad, ("every clean k-of-k count carries an interval or a "
                         "not-independent footnote" if not bad else "; ".join(bad))
    if k == "retraction-consistency":
        def _body(spec):
            """The part of a file a retracted claim must be absent from.

            `path#summary` reads only from the ledger's contributions summary
            onward. The entries above it quote the claims they retract -- that is
            what an append-only record is -- and scanning the whole file would
            make every S-* entry fail the check it exists to satisfy.
            """
            path, _, mode = spec.partition("#")
            if not os.path.exists(path):
                return None
            txt = open(path).read()
            if mode == "summary":
                i = txt.find("## Candidate paper contributions")
                return txt[i:] if i >= 0 else ""
            return txt
        # A paper that narrates its own retractions QUOTES them, and that is the
        # feature rather than the bug: §8 reads `narrower than "cannot have come
        # from the released recipe"`. An occurrence counts as an assertion only
        # when nothing near it marks it as withdrawn.
        WITHDRAWN = ("narrower than", "an earlier draft", "earlier version",
                     "we withdraw", "is retracted", "we retract", "withdrawn",
                     "no longer", "used to", "which Appendix E contradicts")
        hits = []
        for f in exp["files"]:
            body = _body(f)
            if not body:
                continue
            for m in re.finditer(re.escape(exp["retracted"]), body):
                win = body[max(0, m.start() - 260):m.end() + 260].lower()
                if not any(w in win for w in WITHDRAWN):
                    hits.append(f)
                    break
        return not hits, (f'retracted assertion "{exp["retracted"][:44]}" '
                          + (f'STILL ASSERTED in {hits}' if hits
                             else f'absent from all {len(exp["files"])} files'))
    if k == "cross-artifact-sync":
        if not os.path.exists(exp["file"]):
            return False, f'{exp["file"]} does not exist'
        txt = open(exp["file"]).read()
        N = art("paper_numbers.json")
        missing = [key for key in exp["keys"]
                   if key not in N or str(N[key]["value"]) not in txt]
        return not missing, (f'{len(exp["keys"]) - len(missing)}/{len(exp["keys"])} '
                             f'headline values present in {exp["file"]}'
                             + (f'; missing {missing}' if missing else ''))
    if k == "abstract-budget":
        a = paper.split("## Abstract")[1].split("\n## 1.")[0]
        a = re.sub(r"^---\s*$", "", a, flags=re.M)
        words = len(a.split())
        # arXiv identifiers and section cross-references are addresses, not claims
        b = re.sub(r"arXiv:\d{4}\.\d{4,5}\w*", "", a)
        b = re.sub(r"\u00a7\d+(\.\d+)?", "", b)
        nums = re.findall(r"(?<![\w.])\d[\d,]*\.?\d*(?![\w])", b)
        ok = words <= exp["max_words"] and len(nums) <= exp["max_numerals"]
        return ok, (f'{words} words (max {exp["max_words"]}), '
                    f'{len(nums)} numerals (max {exp["max_numerals"]}) {nums}')
    if k == "horizon-consistency":
        # Delegated to scripts/horizon_sweep.py, which is the sweep itself: it
        # walks PAPER.template.md, finds every numeral resolving to a
        # horizon-indexed artifact cell, and reports the horizon that cell came
        # from against the horizon the sentence names. A calibration figure --
        # an overconfidence ratio or a coverage -- must name its horizon in its
        # own sentence; everything else horizon-indexed must name it in the
        # enclosing paragraph. Silence fails either way.
        import horizon_sweep
        findings = horizon_sweep.scan(exp.get("_template"))
        n_s = sum(1 for f in findings if f["scope"] == "sentence")
        return not findings, (
            f'{len(findings)} horizon-unscoped figures ({n_s} calibration, '
            f'{len(findings) - n_s} other)'
            + ("" if not findings else
               "; first: L%d %s %s" % (findings[0]["line"], findings[0]["keys"],
                                       findings[0]["sentence"][:70])))
    if k == "arithmetic":
        # A stated total against the sum of its stated parts, both read as the
        # STRINGS the paper prints -- not as the underlying floats. Rounding is
        # where this class of defect lives: three correct figures, each rounded
        # on its own, and the two parts no longer make the total.
        N = art("paper_numbers.json")
        def _num(key):
            return float(str(N[key]["value"]).replace(",", ""))
        missing = [x for x in [exp["total"]] + exp["parts"] if x not in N]
        if missing:
            return False, f"keys absent from paper_numbers: {missing}"
        tot, parts = _num(exp["total"]), [_num(x) for x in exp["parts"]]
        ok = abs(tot - sum(parts)) <= exp["tol"]
        return ok, (f'{exp["total"]}={tot:g} vs '
                    + " + ".join(f"{p}={v:g}" for p, v in zip(exp["parts"], parts))
                    + f" = {sum(parts):g} (tol {exp['tol']:g})")
    if k == "kind-count":
        # Three counts that must be one: what section 9 claims, what appendix D
        # enumerates, and what this file actually registers at runtime.
        N = art("paper_numbers.json")
        registered = len({c["kind"] for c in CLAIMS})
        claimed = int(exp.get("_forced", N[exp["key"]]["value"]))
        # appendix D enumerates the kinds as *italicised* names in one sentence
        i = paper.find("**The check kinds.**")
        seg = paper[i:paper.find("\n\n", i)] if i >= 0 else ""
        enumerated = len(set(re.findall(r"\*([a-z][a-z-]+)\*", seg)))
        ok = registered == claimed == enumerated and i >= 0
        return ok, (f'registered {registered}, section 9 claims {claimed}, '
                    f'appendix D enumerates {enumerated}')
    if k == "scope-consistency":
        # A universal quantifier over a set the paper enumerates elsewhere. The
        # quantifier is forbidden outright in the named section: "without
        # exception" over eight claims of which appendix E prices two as
        # affordable is not a wording problem, it is a false statement.
        i = paper.find("## " + exp["section"])
        if i < 0:
            return False, f'section {exp["section"]!r} not found'
        j = paper.find("\n## ", i + 4)
        body = paper[i:j if j > 0 else len(paper)]
        hits = [f for f in exp["forbid"] if f in body]
        return not hits, (f'{len(exp["forbid"])} universal quantifiers checked against '
                          f'the enumerated set'
                          + (f'; PRESENT: {hits}' if hits else '; none present'))
    if k == "interval-required":
        N = art("paper_numbers.json")
        bad = []
        for point, interval in exp["quantities"]:
            if interval not in N:
                bad.append(f"{point}: no interval key {interval}")
                continue
            if str(N[interval]["value"]) not in paper:
                bad.append(f"{point}: interval {interval} not quoted in the paper")
        return not bad, (f'{len(exp["quantities"]) - len(bad)}/{len(exp["quantities"])} '
                         f'quoted quantities carry their interval'
                         + (f'; {bad}' if bad else ''))
    raise ValueError(k)


def corruption_for(c):
    """A corruption must INVERT what this claim expects, not set a fixed value.

    The first version of this table set `expect: "disjoint"` for every overlap
    check and `expect: "rise"` for every sign check. For the claims that already
    expected those, the "corruption" was a no-op and the self-test reported the
    check as MISSED -- correctly, since nothing had been corrupted. Two of eleven
    were vacuous. Inverting relative to the claim fixes it, and the extremum case
    now names a real runner-up rather than a label absent from the family, so the
    check has to reject a plausible answer rather than a nonexistent one.
    """
    k = c["kind"]
    if k == "overlap":
        return {"expect": "disjoint" if c["expect"] == "overlap" else "overlap"}
    if k == "sign":
        return {"expect": "rise" if c["expect"] == "fall" else "fall"}
    if k == "orders":
        # C3(rev2), 3.6. This returned None when the claim quotes the ratio
        # directly rather than as an order of magnitude, so one of the 32
        # assertions was exempt from the self-test and nothing said which or
        # why -- the README duly read "31 of 31 caught" beside "32 claims".
        # A directly-quoted ratio is now checked for being IN the sentence that
        # quotes it, which is corruptible: demand a different number.
        if c["stated_orders"] is None:
            # Demand a ratio an order of magnitude away from the real one: a
            # value the sentence cannot contain, unlike "1", which every
            # interval and horizon label in the window supplies for free.
            return {"_forced_quote": f'{10 * dig(*c["num"]) / dig(*c["den"]):,.0f}'}
        return {"stated_orders": c["stated_orders"] + 1}
    if k == "cell":
        return {"expect_observed": dig(*c["cell"])["observed"] + 1}
    if k == "count-consistency":
        if c.get("forbid_variants"):
            # forbid the CANONICAL spelling, which is present everywhere by
            # construction: the check must reject a variant list that catches
            # something rather than one that catches nothing
            return {"forbid_variants": c["forbid_variants"] + [str(dig(*c["value"]))]}
        # corrupt the COUNT, not the path: the check must reject a paper that
        # agrees with itself on a different number than the ledger holds
        return {"_forced": int(dig(*c["value"])) + 1}
    if k == "compare":
        return {"expect": "lt" if c["expect"] == "gt" else "gt"}
    if k == "relvar":
        return {"at_least": c["at_least"] * 100}
    if k == "horizon-label":
        # demand the OTHER horizon's number -- the diagnostic one, which is the
        # exact substitution X-13 found in the shipped paper
        if ".100." in c["must_quote"][1]:
            return {"must_quote": (c["must_quote"][0],
                                   c["must_quote"][1].replace(".100.", ".368."))}
        return {"fmt": "{:.4f}"}
    if k == "horizon-forbidden":
        # plant a label the check would have to reject
        return {"forbid": c["forbid"] + ["open-loop diagnostic"]}
    if k == "count-dependence":
        # name a section that is not there, so the scan cannot vacuously pass
        return {"sections": c["sections"] + ["Nonexistent section"]}
    if k == "retraction-consistency":
        # a string that IS present, standing in for a retracted claim never removed
        return {"retracted": "reproduction"}
    if k == "cross-artifact-sync":
        return {"keys": c["keys"] + ["d1_ratio"], "file": "requirements.txt"}
    if k == "abstract-budget":
        return {"max_words": 10}
    if k == "interval-required":
        return {"quantities": c["quantities"] + [("planted", "no_such_interval_key")]}
    if k == "horizon-consistency":
        # Plant a sentence quoting an h=368 ratio and naming no horizon --
        # exactly the shape of every defect this kind was written for -- and
        # require the scanner to find it.
        return {"_template": open("PAPER.template.md").read()
                + "\n\nThe released checkpoint is {{d1n_alea_ratio_h368}} times "
                  "overconfident on its own error.\n"}
    if k == "arithmetic":
        # Widen one part by more than the tolerance by swapping it for the total.
        return {"parts": c["parts"][:-1] + [c["total"]]}
    if k == "kind-count":
        return {"_forced": len({x["kind"] for x in CLAIMS}) + 1}
    if k == "scope-consistency":
        # A phrase that IS in the section, standing in for a quantifier never
        # removed.
        return {"forbid": c["forbid"] + ["we did not test"]}
    if k == "extremum":
        fam = _family(c["family"])
        ranked = sorted(fam, key=fam.get, reverse=(c["expect"] == "max"))
        runner_up = ranked[1]                       # the second-best, a plausible wrong answer
        if "|" in runner_up:
            q, h, ep = runner_up.split("|")
            return {"named": {"quantity": q, "h": int(h[2:]), "fit_episode": int(ep[2:])}}
        if runner_up.startswith("h=") and runner_up[2:].isdigit():
            return {"named": {"h": runner_up[2:]}}
        return {"named": {"label": runner_up}}
    raise ValueError(k)


def main():
    paper = open(PAPER).read()
    rows, bad = [], 0
    for c in CLAIMS:
        ok, detail = evaluate(c, paper)
        rows.append({"id": c["id"], "kind": c["kind"], "where": c["where"],
                     "says": c["says"], "pass": ok, "detail": detail})
        bad += not ok
    print("PART C — COMPARATIVE CLAIM CHECK")
    print("=" * 104)
    for r in rows:
        print(f"  {'PASS' if r['pass'] else 'FAIL'}  {r['id']:<6} {r['kind']:<9} §{r['where']:<18} {r['detail']}")
    print("=" * 104)
    print(f"  {len(rows) - bad}/{len(rows)} comparative claims verified")

    out = {"n_claims": len(rows), "n_pass": len(rows) - bad, "claims": rows,
           "checker_defects": CHECKER_DEFECTS,
           "kinds": sorted({c["kind"] for c in CLAIMS})}

    if "--self-test" in sys.argv:
        print("\n  SELF-TEST — every check must FAIL when its expectation is corrupted")
        print("  " + "-" * 100)
        st, st_bad = [], 0
        for c in CLAIMS:
            corrupt = corruption_for(c)
            # the orders check that quotes the ratio directly has no stated_orders
            # to corrupt, which is precisely why A5 was fixed that way
            if corrupt is None:
                st.append({"id": c["id"], "skipped": "quotes the ratio directly, "
                                                     "no orders claim to corrupt"})
                print(f"  n/a   {c['id']:<6} quotes the ratio directly — nothing to corrupt")
                continue
            ok, detail = evaluate(c, paper, override=corrupt)
            caught = not ok
            st.append({"id": c["id"], "corruption": str(corrupt), "caught": caught})
            st_bad += not caught
            print(f"  {'caught' if caught else 'MISSED':<6} {c['id']:<6} {detail}")
        print("  " + "-" * 100)
        n = len([x for x in st if "caught" in x])
        print(f"  {n - st_bad}/{n} corruptions caught")
        out["self_test"] = {"n": n, "caught": n - st_bad, "detail": st}
        bad += st_bad

    json.dump(out, open(os.path.join(R.RESULTS, "comparative_claims.json"), "w"), indent=2)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
