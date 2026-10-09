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
_BC_TEMPLATE = "docs/BUILD_CHECKS.template.md"
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


_NIND = re.compile(r"n_independent\s*=\s*\**\s*(\d+)"
                   r"|\b(\d+)\s+(?:\*\*)?(?:non-overlapping|independent|400-step"
                   r"|units\b|trajectories\b)")


def _section_text(paper, sid):
    """The body of the section that owns a claim, as PAPER.md writes it.

    Two shapes, because the paper has two. Most sections are markdown headings
    and end at the next heading of any level. 7.1-7.5 are bold paragraph leads
    inside section 7 rather than headings, so a heading scan alone returns
    nothing for them; those end at the next such lead.
    """
    m = re.search(r"^#{2,3} " + re.escape(sid) + r"(?=[.\s])", paper, re.M)
    if m is not None:
        nxt = re.search(r"^#{2,3} ", paper[m.end():], re.M)
    else:
        m = re.search(r"^\*\*" + re.escape(sid) + r"(?=[.\s])", paper, re.M)
        if m is None:
            return None
        nxt = re.search(r"^(?:\*\*\d+\.\d+(?=[.\s])|#{2,3} )", paper[m.end():], re.M)
    return paper[m.start():m.end() + nxt.start()] if nxt else paper[m.start():]


def _stated_nind(section):
    """Every independent-unit count the section itself states."""
    return {int(a or b) for a, b in _NIND.findall(section)}


def _stated_arenas(section, forms):
    low = section.lower()
    return [lab for lab, fs in forms.items() if any(f in low for f in fs)]


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
    {"id": "C1.1", "kind": "overlap", "where": "6.6",
     "says": "the marginal intervals *do* overlap",
     "a": ("task_d_nind20.json", "d2_forecast_index.128.ci.index"),
     "b": ("task_d_nind20.json", "d2_forecast_index.128.ci.epistemic"),
     "expect": "overlap"},
    {"id": "C1.2", "kind": "overlap", "where": "6.6",
     "says": "excludes zero at",
     "a": ("task_d_nind20.json", "d2_forecast_index.368.ci.index"),
     "b": ("task_d_nind20.json", "d2_forecast_index.368.ci.epistemic"),
     "expect": "disjoint"},
    # ---- C2 extremum (A4) ------------------------------------------------
    {"id": "C2.1", "kind": "extremum", "where": "6.7",
     "says": "The largest deviation over all",
     "family": ("task_d3_perhorizon.json", "d3_cells"),
     "named": {"quantity": "aleatoric", "h": 100, "fit_episode": 8},
     "expect": "max"},
    {"id": "C2.2", "kind": "extremum", "where": "6.6",
     "says": "is the smallest lower bound in the table",
     "family": ("task_d_nind20.json", "d2_paired_lo"),
     "named": {"h": "128"},
     "expect": "min"},
    # ---- C3 sign (A3) ----------------------------------------------------
    {"id": "C3.1", "kind": "sign", "where": "6.6",
     "says": "*lowers* disagreement's correlation by",
     "a": ("task_d2b_robustness.json", "raw.r_disagreement_error"),
     "b": ("task_d2b_robustness.json", "controls.linear.r_disagreement_given_index"),
     "expect": "fall"},
    {"id": "C3.2", "kind": "sign", "where": "6.6",
     "says": "*lowers* disagreement's correlation by",
     "a": ("task_d2b_robustness.json", "raw.r_disagreement_error"),
     "b": ("task_d2b_robustness.json", "controls.linear.r_disagreement_given_index"),
     "expect": "fall"},
    {"id": "C3.3", "kind": "sign", "where": "6.6",
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
    {"id": "C4.3", "kind": "orders", "where": "12",
     "says": "penalises with is better by a factor of",
     "num": ("task_d_nind20.json", "d1_by_horizon.100.aleatoric.ratio_err_over_sigma"),
     "den": ("task_d_nind20.json", "d1_by_horizon.100.epistemic.ratio_err_over_sigma"),
     "stated_orders": None},
    {"id": "C4.2", "kind": "orders", "where": "6.5",
     "says": "a factor of about 10^",
     "num": ("task_b_permutation.json",
             "arenas.in-sample.models.teacher-forced armB.368.p_permutation"),
     "den": ("task_b_permutation.json",
             "arenas.in-sample.models.teacher-forced armB.368.p_binomial_two_sided"),
     "stated_orders": 13},
    # ---- C5 arena / horizon provenance (A1) ------------------------------
    {"id": "C5.1", "kind": "cell", "where": "12",
     "says": "ranking error inversely at h = 368 on every one of",
     "cell": ("task_b_permutation.json",
              "arenas.all-episodes.models.released aleatoric.368"),
     "expect_observed": 0, "expect_n": 45},
    {"id": "C5.2", "kind": "cell", "where": "6.5",
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
    {"id": "C2.3", "kind": "extremum", "where": "6.5",
     "says": "it has the largest mean correlation of the four",
     "family": ("task1_calibration.json", "cal_mean_r"),
     "named": {"label": "teacher-forced armB"}, "expect": "max"},
    {"id": "C2.4", "kind": "extremum", "where": "6.6",
     "says": "it is the largest anywhere in this work",
     "family": ("task_d_nind20.json", "d2_epistemic_r"),
     "named": {"h": "1"}, "expect": "max"},
    {"id": "C2.5", "kind": "extremum", "where": "6.2",
     "says": "the smallest is faithful (mse) h=368",
     "family": ("task_b_permutation.json", "holm_all"),
     "named": {"label": "faithful (mse) h=368"}, "expect": "min"},
    {"id": "C3.4", "kind": "compare", "where": "6.5",
     # Re-anchored in pre-submission S7 (§6.6 reworded); the comparison is unchanged.
     "says": "Nor does it beat Arm B's head on strength",
     "a": ("task_b2_epistemic.json", "by_horizon.368.epistemic.corr_mean"),
     "b": ("task1_calibration.json", "teacher-forced armB.sigma_err_corr_mean"),
     "expect": "lt"},
    {"id": "C3.5", "kind": "compare", "where": "6.5",
     "says": "which already exceeds the smallest Holm threshold",
     "a": ("task_b_permutation.json", "arenas.out-of-sample.p_floor"),
     "b": ("task_b_permutation.json", "arenas.out-of-sample.holm.smallest_threshold"),
     "expect": "gt"},
    {"id": "C3.6", "kind": "compare", "where": "9",
     "says": "ranks whole rollouts almost perfectly",
     "a": ("task_d_nind20.json", "d2_forecast_index.1.r_epistemic"),
     "b": ("task_d_nind20.json", "d2_forecast_index.368.r_epistemic"),
     "expect": "gt"},
    # D2 moved these. The abstract's retraction sentence is gone -- abstract space
    # is for results -- and §1's paragraph is one sentence with a pointer, so the
    # sites are now §9 and appendix D, which is where D2 says they belong. The
    # kind is unchanged and so is what it asserts; only the list of places the
    # count must agree in has moved, and it has to move with the prose or it
    # guards nothing.
    {"id": "C7.1", "kind": "count-consistency", "where": "8 / BUILD_CHECKS",
     "surface": ["docs/BUILD_CHECKS.md"],
     # Re-anchored in pre-submission S5 (item 8): the introduction, section 8, the README
     # and the supplement now share one vocabulary -- claims withdrawn on evidence,
     # framings withdrawn, superseded entries -- counted by scripts/ledger_check.py.
     "label": "claims withdrawn on evidence",
     "says": "claims withdrawn on evidence**, and",
     "value": ("paper_numbers.json", "n_retractions.value"),
     "sites": ["each beside the evidence that withdrew it:",
               "claims withdrawn on evidence**, and",
               "claims withdrawn on evidence, in order"]},
    {"id": "C7.2", "kind": "count-consistency", "where": "8 / BUILD_CHECKS",
     "surface": ["docs/BUILD_CHECKS.md"],
     # Re-anchored in pre-submission S5 (item 8): the introduction, section 8, the README
     # and the supplement now share one vocabulary -- claims withdrawn on evidence,
     # framings withdrawn, superseded entries -- counted by scripts/ledger_check.py.
     "label": "framings withdrawn",
     "says": "framings withdrawn rather than numbers",
     "value": ("paper_numbers.json", "n_retract_framing.value"),
     "sites": ["framings withdrawn, and the rest early hypotheses",
               "framings withdrawn rather than numbers",
               "framings withdrawn**, as stated claims"]},
    # ...and the TOTAL, which is what §1 now states and the contributions list
    # repeats. A count that moved out of two places into two others is exactly
    # where a count-consistency defect gets in.
    # The count is stated ONCE in §1 now -- in the contributions list. §1's prose
    # paragraph said it too, which is the duplication D2 was meant to remove and
    # did not: it compressed the paragraph and left the number in both places.
    {"id": "C7.5", "kind": "count-consistency", "where": "1 / 8",
     # Re-anchored in pre-submission S5 (item 8): the introduction, section 8, the README
     # and the supplement now share one vocabulary -- claims withdrawn on evidence,
     # framings withdrawn, superseded entries -- counted by scripts/ledger_check.py.
     # The introduction no longer prints the combined total (n_retract_total), which
     # was the fourth way of counting; it states the superseded-entry count instead, and
     # this check follows that assertion into both places it is made.
     "label": "superseded entries",
     "says": "superseded entries, each beside the evidence",
     "value": ("paper_numbers.json", "n_superseded.value"),
     "sites": ["superseded entries, each beside the evidence",
               "superseded entries kept in the record"]},
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
     "surface": ["docs/BUILD_CHECKS.md"],
     "says": "open-loop diagnostic",
     "forbid": ["deployment horizon of h = 368", "368-step deployment horizon",
                "at the 368-step deployment horizon"]},

    # ---- C9 count-dependence ---------------------------------------------
    # "368 of 368 forecast steps" and "10 of 10 held-out cells" invite the
    # independent-trials reading this paper elsewhere warns against. A k-of-N
    # count in the abstract, the lessons or the conclusion must carry an
    # interval beside it or a footnote saying the units are not independent.
    {"id": "C9.1", "kind": "count-dependence", "where": "abstract / 9 / 12",
     # Re-anchored in pre-submission S4: the abstract, §9 and §12 were rewritten (item 3's
     # "unseen by the multiplier / by the model" caveat and PLAN Appendix A's abstract), and
     # the old fragment went with them. The scan itself -- clean k-of-k counts in these three
     # sections -- is unchanged.
     "says": "A per-horizon rescaling brings the released checkpoint's coverage within",
     "sections": ["Abstract", "9. Actionable lessons", "12. Conclusion"]},

    # ---- C10 retraction-consistency --------------------------------------
    # docs/BUILD_CHECKS.template.md joined this list in Session 5a. It did not
    # need to be here before: the text it holds was inside Appendix C, and
    # PAPER.template.md was scanned whole. Moving that text out of the paper moved
    # it out of the scan, which would have left a reader-facing surface where a
    # retracted claim could survive unnoticed -- S-19's own lesson, and the same
    # shape as the Hugging Face model card that no check reads.
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
    {"id": "C10.1", "kind": "retraction-consistency", "where": "7.5 / README / RESULTS",
     "says": "the released artifacts do not reproduce the released",
     "retracted": "cannot have come from the released recipe",
     "files": ["PAPER.template.md", "docs/BUILD_CHECKS.template.md",
               "README.md", "MODEL_CARD.md", "RESULTS.md",
               "FINDINGS_LEDGER.md#summary"]},
    {"id": "C10.2", "kind": "retraction-consistency", "where": "6.5 / README",
     "says": "no per-dimension count in this paper reaches significance",
     "retracted": "sign test on 45 dimensions",
     "files": ["PAPER.template.md", "docs/BUILD_CHECKS.template.md",
               "README.md", "MODEL_CARD.md", "RESULTS.md"]},
    {"id": "C10.3", "kind": "retraction-consistency", "where": "6.7",
     "says": "The two largest deviations are both on the",
     "retracted": "deviations are both at h=100 on the aleatoric term, in opposite directions",
     "files": ["PAPER.template.md", "docs/BUILD_CHECKS.template.md",
               "README.md", "MODEL_CARD.md", "RESULTS.md"]},
    {"id": "C10.4", "kind": "retraction-consistency", "where": "4",
     "says": "are claims about policy learning or hardware",
     "retracted": "without exception",
     "files": ["PAPER.template.md", "docs/BUILD_CHECKS.template.md",
               "README.md", "MODEL_CARD.md", "RESULTS.md"]},
    # C10.5 extends the C10 group from "is a retracted claim still asserted" to
    # "is a retraction filed under the class the ledger gives it". S-15 was filed
    # under both: appendix C lists it among the framing retractions, which is
    # what the ledger's `**Retracts**` line makes it, and section 8 called it
    # "the most consequential of those" in a paragraph that had just named both
    # classes, so the antecedent resolved either way. The paper reads as PAPER.md
    # rather than the template here, because appendix C's enumeration is
    # generated from the ledger and does not exist in the source.
    # B4: the generated enumeration left PAPER.md for docs/BUILD_CHECKS.md, and with
    # only the template listed this claim fell from 19 namings to 9 while passing.
    {"id": "C10.5", "kind": "retraction_class_consistency", "where": "8 / BUILD_CHECKS",
     # Re-anchored in pre-submission S5 (item 8): the introduction, section 8, the README
     # and the supplement now share one vocabulary -- claims withdrawn on evidence,
     # framings withdrawn, superseded entries -- counted by scripts/ledger_check.py.
     "says": "The most consequential of the framings withdrawn",
     "files": ["PAPER.md", "docs/BUILD_CHECKS.template.md", "docs/BUILD_CHECKS.md",
               "README.md", "MODEL_CARD.md", "RESULTS.md"]},

    # ---- C11 cross-artifact-sync -----------------------------------------
    # README and MODEL_CARD are reader-facing and were materially behind the
    # paper: 17 training runs against 24, 4,804 regenerated values against
    # 6,073, a headline the paper had reframed.
    {"id": "C11.1", "kind": "cross-artifact-sync", "where": "README",
     "surface": ["docs/BUILD_CHECKS.md"],
     "says": "deliberately corrupted expectation",
     # C3(rev2): the page count is here because the README quoted "9 pages" for a
     # 30-page PDF for two revisions, and nothing compared them. It moves every
     # time the paper grows, which is exactly the property that made it drift.
     # S5: the README prints the lower-case form now, and the superseded count joins.
     "keys": ["n_runs", "ver_values", "ver_files", "pdf_pages",
              "n_retractions_lower", "n_retract_framing_word", "n_superseded"],
     "file": "README.md"},
    # The external-read brief is a hand-written document that quotes the paper's
    # headline figures, and it drifted within hours of being written: it still
    # said "46.3 hours across 26 runs" after M-49's five capacity-matched runs
    # landed, and described E5 and E7 as not yet run. A document that misdescribes
    # the paper is worse than none, because the reader it is written for takes it
    # as the paper's own account of itself.
    {"id": "C11.3", "kind": "cross-artifact-sync", "where": "EXTERNAL_READ_BRIEF",
     "surface": ["docs/BUILD_CHECKS.md"],
     "says": "deliberately corrupted expectation",
     "keys": ["rt_hours", "rt_runs", "d1_ratio", "d1n_epi_ratio_h1",
              "d1n_epi_cov1_h1", "v3_cov_nominal1", "a2_rdd", "stale_pct",
              "v1_shared_pct", "m44_ratio_gain", "m49_ratio_gain",
              "e7_step_r", "e7_r_dis", "e5s_span", "e5s_mse_under",
              # S5: the brief now gives S-20's replacement figures, the Arm A count and the
              # ledger's withdrawal counts; each must still match the artifact.
              "ad_nrmse", "ad_nrmse_ci", "ad_rel", "ad_rel_ci", "d3x_own_epi_ok",
              "n_retractions_lower", "n_retract_framing_word", "n_superseded"],
     "file": "docs/EXTERNAL_READ_BRIEF.md"},
    {"id": "C11.2", "kind": "cross-artifact-sync", "where": "MODEL_CARD",
     "surface": ["docs/BUILD_CHECKS.md"],
     "says": "deliberately corrupted expectation",
     "keys": ["d1n_epi_ratio_h100", "e5_ratio_h100", "m44_ratio_gain",
              "r2_indep_ratio_h100"],
     "file": "MODEL_CARD.md"},

    # docs/BUILD_CHECKS.md became a reader-facing surface in 5a when Appendix C's
    # machinery moved there. It is generated from the same results/paper_numbers.json the
    # paper is, so a count quoted there cannot drift from the one §8 prints -- but that is
    # a property of the build, and this asserts it rather than trusting it.
    #
    # docs/APPENDIX_G_RULES.md is deliberately NOT here. It carries no substituted values:
    # appendix_g_rules.py writes it straight from FINDINGS_LEDGER.md in the same pass that
    # writes the body table, so the two cannot disagree by construction. A sync claim over
    # it would match on incidental substrings and assert nothing.
    {"id": "C11.4", "kind": "cross-artifact-sync", "where": "BUILD_CHECKS",
     "surface": ["docs/BUILD_CHECKS.md"],
     "says": "deliberately corrupted expectation",
     "keys": ["cc_n", "cc_kinds", "cc_st_caught", "cc_selfdefects_word"],
     "file": "docs/BUILD_CHECKS.md"},

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
    #
    # C1(rev3): 262 to 324 words and 13 to 15 numerals. This is the second
    # deliberate raise and it is larger than the first, so the reason is set out
    # rather than asserted. Four things were ADDED to the abstract under the
    # revision brief, against one removal:
    #
    #   E1  the calibration claim now LEADS with h = 1, and says in the abstract
    #       that the failure is not accumulated rollout error. That objection --
    #       a per-step conditional sigma is not an estimate of open-loop
    #       accumulated error -- is the first thing a reviewer raises, and
    #       meeting it in the abstract is worth more than the words it costs.
    #   E2  the ranking claim now carries its two qualifications: the evidence is
    #       in-sample for a checkpoint trained on all ten episodes, and the
    #       pre-registered replication on our own models returned DOES NOT
    #       GENERALISE. Both were in §6.7 and §12 and neither reached the
    #       abstract, which is exactly the shape of an abstract a reader feels
    #       managed by.
    #   D4  §7.2's action-alignment defect, which is the most immediately useful
    #       finding here for anyone using the released repository.
    #   B8  the provenance sentence, which now states what the build ENFORCES
    #       rather than the false claim it replaced.
    #   D2  the retraction sentence was removed; abstract space is for results.
    #
    # The budget exists so the abstract stays readable, not so it stays short at
    # the cost of qualifications the body already makes. 322 words is the tightest
    # this content compresses to; two full passes were spent getting there from
    # 379. The cap is set 2 above it so an ordinary rewording does not fail the
    # build, and not so far above that the next addition goes unnoticed.
    #
    # C1(rev3, second pass): 324 to 346 words, 15 to 16 numerals. The abstract grew
    # because the PAPER grew two results, not because the prose loosened:
    #
    #   E5  §6.3's mechanism claim is now demonstrated against ground truth
    #       rather than derived and inferred. The abstract says so in one clause
    #       and two numerals, and it is the sentence that removes the follow-up's
    #       own competing explanation ("small stochasticity in the environment").
    #   E7  the ranking claim gained a third limit, and it is the one a reviewer
    #       would otherwise find: a FREE baseline ranks error close enough to the
    #       five-member ensemble that this sample cannot separate them. Stated
    #       qualitatively and costing no numeral, because the comparison matters
    #       and the two figures belong in §6.7.
    #
    # Two full trim passes were spent getting from 361 to 344, and the cap is set
    # two above that rather than at a round number, so the next addition fails the
    # build and has to be argued for as these were.
    {"id": "C12.1", "kind": "abstract-budget", "where": "abstract",
     "says": "The base paper's central training claim reproduces",
     # +4 words, +1 numeral, and this raise is a CORRECTNESS fix rather than added
     # content. The abstract quoted §7.2's alignment defect as "overstating the
     # checkpoint's own error by 75%", naming neither the metric nor the horizon.
     # It is nRMSE at h = 368 and nothing else: the same comparison gives 50.9% at
     # h = 1, 10.9% at h = 128, and 9.5% on relative-L1 -- the metric the
     # abstract's OWN first headline uses. A reviewer checking it against
     # relative-L1 would compute a number eight times smaller and conclude the
     # abstract was wrong. Naming both scopes costs the numeral 368 and four words.
     #
     # A second correctness fix, +19 words and +1 numeral. The provenance sentence
     # read "Every quantity here is substituted from a named artifact". Still too
     # strong: the abstract itself types "sigma = 0" and "all ten episodes", and
     # 167 of the 552 typed numerals sit under declared exceptions. What the build
     # actually enforces is narrower and is now what the abstract says -- every
     # MEASUREMENT is substituted, and every numeral that is not one is classified
     # as an address, a horizon label or a declared constant, with the build
     # failing on anything left over. B8 replaced a false claim with an
     # over-strong one; this replaces it with the enforced one.
     #
     # Pre-submission S4 (2026-09-28): the abstract went from 17 numerals and 237 words to
     # 26 and 330, and the cap from 18 to 26.
     # This fourth raise is the first argued outside the check, and the reason is a
     # ruling rather than a trim. The plan asked for its Appendix A abstract with
     # every listed number bound, and for the alignment sentence on S3's independent
     # figures in both metrics with both intervals; together that is 26. Asked, the
     # user ruled "Full Appendix A; raise cap"
     # (docs/presubmission/DECISIONS_FOR_USER.md#S4-abstract-budget). The cap is set
     # AT the installed count, not above it, so the next addition fails the build and
     # has to be argued for as these were. The word cap is unchanged; the plan's own
     # limit, 330, is tighter and the abstract meets it.
     "max_words": 370, "max_numerals": 26},

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
    {"id": "C7.3", "kind": "count-consistency", "where": "3.1 / 6.7 / Figure 1",
     "label": "nominal coverage at ±1σ",
     "says": "the calibrated targets are",
     "value": ("paper_numbers.json", "v3_cov_nominal1.value"),
     "sites": [], "forbid_variants": ["68.3%", "68.3\\%", "68.3 %"],
     "files": ["PAPER.md", "PAPER.tex", "docs/BUILD_CHECKS.md",
               "README.md", "MODEL_CARD.md"]},
    {"id": "C7.4", "kind": "count-consistency", "where": "6.6 / 10",
     "label": "the h=1 disagreement interval",
     "says": "it is the largest anywhere in this work",
     "value": ("paper_numbers.json", "d2_epi_ci_h1.value"),
     "sites": [], "forbid_variants": ["+0.917"],
     "files": ["PAPER.md", "docs/BUILD_CHECKS.md", "README.md", "MODEL_CARD.md"]},

    # ---- C3.7: the sign check that should have caught 3.1 -----------------
    # 6.8 said the two largest held-out deviations were "in opposite
    # directions". Both are above target. No `sign` claim covered the sentence
    # -- the kind existed and the assertion was never written -- which is the
    # third defect the self-test has found in the checker rather than the paper.
    {"id": "C3.7", "kind": "sign", "where": "6.7",
     "says": "The two largest deviations are both on the",
     "a": ("task_d3_perhorizon.json", "target_coverage"),
     "b": ("paper_numbers.json", "d3_worst_cov.value"),
     "expect": "rise", "_scale_b": 0.01},
    {"id": "C3.8", "kind": "sign", "where": "6.7",
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
    {"id": "C15.3", "kind": "arithmetic", "where": "4 / Appendix D",
     "says": "claims we tested, the original reports no quantitative",
     "total": "appF_n_claims", "parts": ["orig_n_tested", "n_untested"], "tol": 0},
    {"id": "C15.4", "kind": "arithmetic", "where": "4 / Appendix C",
     "says": "are claims about policy learning or hardware",
     "total": "n_untested", "parts": ["appE_n_sim", "appE_n_cpu"], "tol": 0},
    # Appendix B's CPU budget carried a third figure -- the capacity-matched arm's
    # hours -- that C15.1 could not see, because those hours are a subset of the
    # total rather than a further part of the iteration-length split. Stated
    # beside a total it does not visibly sum with, it is free to drift. The
    # partition that does hold is total = matched + released, and it is asserted.
    {"id": "C15.5", "kind": "arithmetic", "where": "Appendix B",
     "says": "runs at the released width, and the two parts are asserted to make the total",
     "total": "rt_hours",
     "parts": ["rt_hours_m49", "rt_hours_released"], "tol": 0.05},

    # ---- C16 kind-count ---------------------------------------------------
    # Section 9 said "N kinds" from a generated key while appendix D enumerated
    # eight by hand. They had drifted seven apart, inside the appendix whose
    # subject is count consistency.
    # B4: the anchor was "verifies", which first matches a sentence of section 2
    # that has nothing to do with the kind count, so it pinned nothing. It is now
    # the moved sentence that states the count.
    {"id": "C16.1", "kind": "kind-count", "where": "BUILD_CHECKS",
     "surface": ["docs/BUILD_CHECKS.md"],
     "says": "comparative claims** across", "key": "cc_kinds"},

    # ---- C20 unit-consistency ---------------------------------------------
    # NEW in Session 6. This revision introduced a SECOND evaluation unit: M-64 rebuilds
    # §5 and §6.7 at 32+h rows against the 400-step trajectories everything else uses, and
    # §5's h=1 now has two readings that are both true at their own n. An "n_independent =
    # 60" that does not say what one of those sixty IS cannot be checked by a reader, and
    # the two readings cannot be told apart. Every n_independent figure in the prose must
    # name its unit within the sentence that states it.
    {"id": "C20.1", "kind": "unit-consistency", "where": "whole paper",
     "says": "n_independent",
     # A sentence naming an n_independent satisfies this by containing any of these.
     "unit_markers": ["400-step", "400 rows", "32+h", "-row unit", "short unit",
                      "trajector", "unit level", "unit-level", "non-overlapping"]},

    # ---- C17 scope-consistency -------------------------------------------
    # Section 4 said the eight untested claims were "without exception" about
    # policy learning or hardware. Appendix D says of two of them "no simulator
    # needed" and puts both within CPU reach. A universal quantifier in the body
    # has to be checked against the set it quantifies over.
    # ---- C18 frequency-consistency ---------------------------------------
    # A stated FREQUENCY is a claim about a count, and no kind bound one to a
    # recomputed count. §6.7 said the distinction between the marginal and the
    # paired test "matters at exactly one place"; adding h=100 to the grid made
    # it two, and the sentence carrying that error was the one recording the
    # previous version of the same error. count-consistency compares a count
    # against the ledger; this compares a WORD against a relation recomputed
    # from the artifacts.
    {"id": "C18.1", "kind": "frequency-consistency", "where": "9",
     "says": "on a paired test that excludes zero at",
     "count": ("paper_numbers.json", "d2p_n_separating.value"),
     "total": ("paper_numbers.json", "d2p_n_horizons.value"),
     "expect": "all", "span": 220},
    {"id": "C18.2", "kind": "frequency-consistency", "where": "6.6",
     "says": "Disagreement wins at every horizon tested",
     "count": ("paper_numbers.json", "d2b_n_index_wins.value"),
     "total": ("paper_numbers.json", "d2b_n_horizons_tested.value"),
     "expect": "none", "span": 200},
    {"id": "C18.3", "kind": "frequency-consistency", "where": "6.8",
     "says": "conditions hold, against every one of the",
     "count": ("paper_numbers.json", "m44_n_conditions_met.value"),
     "total": ("paper_numbers.json", "m44_n_conditions.value"),
     "expect": "all", "span": 140},

    # ---- C19 restatement --------------------------------------------------
    # THE class this revision exists for, and the one none of the twenty kinds
    # above could see. Every kind here verifies a sentence against the artifact
    # in the section that COMPUTES it. None looks at a sentence restating a
    # quantity another section owns, and all four defects an independent reader
    # found by hand were of exactly that shape. Delegated to
    # scripts/restatement_index.py, which also carries an acceptance run against
    # the drafts each defect stood in -- a check validated only against the tree
    # it was written from is the vacuous assertion recorded four times above.
    {"id": "C19.1", "kind": "restatement", "where": "whole paper",
     "says": "Curves are reported at"},

    {"id": "C17.1", "kind": "scope-consistency", "where": "4 / Appendix C",
     # S9 re-anchor: the two claims this sentence called within CPU reach were run (§5.2, §5.3),
     # and §4 now says every untested claim needs a simulator or hardware. paper_numbers.py asserts that
     # no untested Appendix D row is tagged `cpu`, which is what makes that universal true.
     "says": "we did not test needs a simulator or hardware we do not have",
     "section": "4. What the original papers claim, and which claims we test",
     "forbid": ["without exception", "in all cases", "in every case",
                "all eight", "none of the eight", "each of the eight"]},

    # ---- C21 figure_reference ---------------------------------------------
    # Every in-text figure reference in the shipped paper pointed at the wrong
    # figure. The prose cited the digit in the figure's FILENAME while LaTeX
    # numbers by order of appearance, and the two orders differ: paper_fig4_* is
    # the first figure the prose refers to and renders as Figure 1. Twelve sites,
    # every one of them wrong, and none of the twenty-two kinds above could see
    # it because no kind knew how many figures the document has.
    {"id": "C21.1", "kind": "figure_reference", "where": "whole paper",
     "says": "This is the same computation Figure 1 plots"},

    # ---- C22 population_partition -----------------------------------------
    # Section 6.3 opened "across all 26 runs the collapse is linear", said four
    # sentences later that Figure 4(a) "shows all 31 runs", and then headed a
    # table "The 31 runs, so a reader can count them" -- and the figure plots 26.
    # The table had no width column, so M-49's five capacity-matched runs sat
    # inside the released-width Arm A row as a ten-seed entry reading
    # 0, 0, 1, 1, 2, 2, 3, 3, 4, 4. Every numeral came from an artifact and every
    # one was right about its own population; nothing asserted that the three
    # populations partition, so the paper could and did quote them against each
    # other. The table a reader is invited to count is checked by counting it.
    {"id": "C22.1", "kind": "population_partition", "where": "6.3 / Appendix B",
     # Re-anchored in pre-submission S7: §6.3's lead-in to the run table was shortened; the
     # partition this checks (total = family + off-width; fitted + excluded) is unchanged.
     "says": "with the width column separating the collapse family",
     "total": "run_total", "family": "n_runs", "excluded": "n_runs_offwidth",
     "fitted": "e2_fitted_runs", "fitted_excluded": "e2_excluded_10k",
     "table": "run_table", "figure_family": ("paper_figures.json", "fig3", "n_runs")},

    # ---- C23 table_renders -------------------------------------------------
    # Appendices D, E and F reached the PDF at 2.48pt, 0.78pt and 2.80pt against
    # 9.96pt body text. `l` columns never wrap, so a table whose cells are
    # paragraphs set to eleven times the text block and the \resizebox around the
    # tabular shrank the whole thing to fit. Every cell was in the text layer --
    # which is why an extraction of the PDF reads those appendices as
    # run-together prose, and why no check that reads text could see it. This one
    # compares the tables the converter WROTE against the tables the source HAS:
    # the same number of them, each carrying at least one row separator per
    # source row. It does not measure type size; it catches a table that lost
    # rows on the way to LaTeX, which is the failure a reader cannot recover from.
    {"id": "C23.1", "kind": "table_renders", "where": "Appendix C / D / E",
     "says": "checkable row by row"},

    # ---- C24 arena_consistency ---------------------------------------------
    # 3.2's evidence table states an arena and an n_independent for every
    # headline claim, in one place, ahead of the sections that make them. That
    # is a second statement of a fact each section already states, and a second
    # statement of a fact is the shape every restatement defect in this project
    # has had. Nothing above can see it: the numerals are all substituted, so
    # the typed-numeral audit passes, and no kind compares a summary row against
    # the section it summarises. This one does -- for each row, the arena the
    # table gives must be an arena its own section names, and the n_independent
    # must be one the section states. Sections that name neither (6.10 and 7.2
    # state no arena at all) are reported as unconfirmed rather than silently
    # counted as passing.
    # Round 3, R6 (ruling V5): the table moved to Appendix D as its second table; §3.2 keeps the
    # paragraph that points to it, and the anchor sentence with it. Label "3.2" -> "3.2 / Appendix D".
    {"id": "C24.1", "kind": "arena_consistency", "where": "3.2 / Appendix D",
     # S10 re-anchor (user ruling D2 added the checkpoint column and reworded this sentence)
     "says": "so no arena label, sample size or checkpoint in it is typed by hand"},

    # ---- C25 (round 2, T3 item 7) -------------------------------------------------------------
    # C25.1: rule M-23 was run on ONE seed (seed m23_seed); the three-seed d1_ratio and the a1_*_h368
    # table cells extend it and carry none of its weight (Annex 2, E4). A sentence quoting them within
    # two lines of "rule" or "pre-register" must therefore name the seed or the three-seed extension, in
    # its own paragraph or the next one (a table's caption sentence follows the table).
    {"id": "C25.1", "kind": "rule-seed-scope", "where": "abstract / contributions / 5 / 11",
     "says": "the rule's horizon",
     "files": ["PAPER.template.md", "docs/BUILD_CHECKS.template.md", "README.template.md"],
     "keys_regex": r"d1_ratio|a1_[A-Za-z_]*h368", "trigger_regex": r"\brules?\b|pre-regist",
     "window_lines": 2,
     # T3 review F2: "{{d1_seeds}} seeds" and "three seeds" were markers, and they pass the very
     # text this check exists to catch ("over 3 seeds" does not say the rule ran on one). Only
     # phrases that name the rule's seed, or call the three seeds an extension, count.
     # Whitespace-tolerant: the abstract's "one seed per arm" wraps across a line break.
     "marker_regex": r"\{\{m23_seed\}\}|one\s+seed\s+per\s+arm|three-seed\s+extension|extends?\s+(it|the\s+rule)"},
    # C25.2: the alignment defect's cost is small and not consistent in sign at h = 368 (S-20, R-76). No
    # sentence may pair "overstat..." with an alignment figure unless its paragraph names the reversal.
    # Round 3, R3 re-anchor (PLAN 1.2 rule 8): section 7.2 no longer says the evaluation "overstates" the checkpoint's
    # error; it leads with the all-ten-episodes curve (Annex 2 E2). Old anchor "overstates the released checkpoint's
    # error" -> new anchor "What the stale pairing costs depends on the horizon", the paragraph the check guards. The
    # files and the rule are unchanged, and figure_regex now also covers the new all-ten keys (adh20_*), so a sentence
    # pairing "overstat" with one of them is caught too: coverage grows, it does not shrink.
    {"id": "C25.2", "kind": "overstat-reversal", "where": "7.2 / abstract / contributions",
     "says": "What the stale pairing costs depends on the horizon",
     "files": ["PAPER.template.md", "docs/BUILD_CHECKS.template.md", "README.template.md"],
     "figure_regex": r"ad(?:20|h20|h)?_[A-Za-z0-9_]+|stale_[A-Za-z0-9_]+",
     "reversal_regex": r"revers|not consistent in sign"},

    # ---- C26 (round 3, R2: guard G1) ----------------------------------------------------------
    # The 4 Oct draft's abstract, contribution 3 and Appendix D said the best longer forecast beat the original's
    # setting "even when that setting trains twice as long". The body's equal-compute readings split (Appendix U):
    # trained longer, the centre passes each winner on at least one reading. Round 2's plan had chosen that wording
    # from one held-out reading. G1 has two halves. No rendered file may carry that phrasing ("trains twice as long",
    # or "even when" within twelve words of "centre" or "setting"). And a front-matter sentence (abstract,
    # contributions, Appendix D, section 12) that names compute or longer training must say the ranking depends on
    # it or name the split.
    {"id": "C26.1", "kind": "compute-claim", "where": "abstract / contributions / Appendix D / 12",
     # Round 3, R6 re-anchor: the abstract's "so" became a colon to fit rule 10's wording in C12.1's budget.
     "says": "the ranking depends on training budget",
     "files": ["PAPER.md", "README.md", "MODEL_CARD.md", "docs/BUILD_CHECKS.md",
               "docs/APPENDIX_G_VARIANCE_ARITHMETIC.md"],
     "forbidden_regex": r"trains\s+twice\s+as\s+long|\beven\s+when\b(?:\W+\w+){0,12}?\W+(?:centre|center|setting)\b",
     "compute_regex": r"\bcompute\b|\btrain(?:ed|s)\s+longer\b",
     "qualifier_regex": r"\bdepends\b|\bchanges\b|\bsome\s+reading\b|\bat\s+least\s+one\s+reading\b|\bsplit\b"},

    # ---- C27 (round 3, R3: guards G2 and G3) ---------------------------------------------------
    # G2: the 4 Oct draft described the alignment defect's cost from the held-out pair's 4 trajectories ("inflating
    # error mainly at short horizons"), when all ten episodes' 20 describe this checkpoint better (Annex 2 E2). A
    # sentence that names the defect and a short-horizon cost must have the all-ten-episodes figures, or the words, in
    # its paragraph. Sentences end at full stops only, so a clause joined by a semicolon is tested with its neighbour.
    {"id": "C27.1", "kind": "alignment-arena", "where": "abstract / contributions / 3.1 / 7.2",
     # Round 3, R6 re-anchor (rule 10): the abstract names the metric whose rise resolves at h = 1.
     "says": "over all ten episodes this raises the checkpoint's short-horizon relative-L1 error",
     "files": ["PAPER.template.md", "README.template.md", "docs/BUILD_CHECKS.template.md"],
     "defect_regex": r"\bstale\b|misaligned|previous step's action|\balignment\b",
     "short_regex": r"short[\s-]horizons?|\bup to\b|\bh = 1\b",
     "all_ten_regex": r"\{\{(?:adh20|ad20)_\w+\}\}|all ten episodes"},
    # G3: round 2 quoted Arm A's stale-pairing sensitivity as evidence our models barely respond to the action; the
    # figure was void (S-21) and rule X2 measured the response. A paragraph citing stale_armA_* must carry an X2 key.
    {"id": "C27.2", "kind": "action-response", "where": "7.2 / model card",
     "says": "They respond to the action",
     "files": ["PAPER.template.md", "README.template.md", "docs/BUILD_CHECKS.template.md", "scripts/build_model_card.py"]},
]


def _front_matter_regions(paper):
    """The front matter rule 10 of round 3's plan names: the abstract, the contributions list, Appendix D and
    section 12, each as one string, from the rendered PAPER.md."""
    out = {"abstract": paper.split("## Abstract", 1)[1].split("\n## 1.", 1)[0]}
    i = paper.index("**Contributions.**")
    m = re.search(r"\n\n(?![-\s])", paper[i:])
    out["contributions"] = paper[i:i + m.start()]
    for name, head in (("appendix_d", "## Appendix D"), ("conclusion", "## 12. Conclusion")):
        j = paper.index(head)
        k = paper.find("\n## ", j + len(head))
        out[name] = paper[j:k if k > 0 else len(paper)]
    return out


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
                     "no longer", "used to", "which Appendix D contradicts")
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
    if k == "retraction_class_consistency":
        # The ledger decides an S-* entry's class, from its own `**Retracts**`
        # line: a numbered claim retracted on our evidence, a framing withdrawn
        # as a stated claim, or an early hypothesis. Every naming of an entry in
        # a reader-facing file must resolve to exactly one of those, and to the
        # one the ledger gives.
        _led = open("FINDINGS_LEDGER.md").read()
        cls = {}
        for sid in re.findall(r"^### (S-\d+) ", _led, re.M):
            blk = _led[_led.index("### " + sid + " "):]
            blk = blk[:blk.find("\n### ", 5)] if "\n### " in blk[5:] else blk
            m = re.search(r"^\*\*Retracts\*\* (.+)$", blk, re.M)
            if not m:
                continue
            tail = m.group(1).lstrip()
            cls[sid] = ("evidence" if not tail.startswith("—")
                        else "hypothesis" if "early hypothesis" in tail
                        else "framing")
        # Round 2 (ruling U1): an S- entry's **Retracts** line can never be edited, so a later entry
        # may reclassify it with `**Reclassifies** \`S-NN\` as <class>` (M-82 moves S-20 to evidence).
        # Read with ledger_check.py's own pattern, so the two cannot disagree about a class.
        for m in re.finditer(r"^\*\*Reclassifies\*\* `(S-\d+)` as (evidence|framing|early hypothesis)\s*$",
                             _led, re.M):
            cls[m.group(1)] = "hypothesis" if m.group(2) == "early hypothesis" else m.group(2)
        cls.update(exp.get("_forced_ledger", {}))
        MARK = {"framing": r"framings?\b",
                "evidence": r"numbered retractions?|own evidence"
                            r"|our own \*\*numbered claims\*\*"
                            # S5: the new vocabulary's name for the class
                            r"|withdrawn on evidence"}
        bad, seen = [], 0
        for f in exp["files"]:
            if not os.path.exists(f):
                continue
            for para in re.split(r"\n\s*\n", open(f).read()):
                if "S-" not in para:
                    continue
                # The paragraph is scanned as well as the sentence: a sentence
                # that names no class is fine on its own, and is exactly the
                # section 8 defect when the paragraph around it names two.
                pc = {x for x, p in MARK.items() if re.search(p, para, re.I)}
                for sent in re.split(r"(?<=[.:;])\s+", para.replace("\n", " ")):
                    ids = sorted({x for x in re.findall(r"S-\d+", sent) if x in cls})
                    if not ids:
                        continue
                    sc = {x for x, p in MARK.items() if re.search(p, sent, re.I)}
                    for sid in ids:
                        seen += 1
                        if len(sc) > 1:
                            bad.append(f"{f}: {sid} named as {sorted(sc)} in one sentence")
                        elif sc and cls[sid] not in sc:
                            bad.append(f"{f}: {sid} called {sorted(sc)[0]}, "
                                       f"ledger says {cls[sid]}")
                        elif not sc and len(pc) > 1:
                            bad.append(f"{f}: {sid}'s class is left to an antecedent "
                                       f"in a paragraph naming {sorted(pc)}")
                        elif not sc and pc and cls[sid] not in pc:
                            bad.append(f"{f}: {sid} in a paragraph about "
                                       f"{sorted(pc)[0]}, ledger says {cls[sid]}")
        return not bad, (f'{seen} namings of {len(cls)} ledger retractions, each '
                         f'resolving to the ledger\'s class' if not bad
                         else "; ".join(bad[:4]))
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
        # B4: section 8's block and Appendix C moved to the supplementary, and a
        # whole-paper sweep over PAPER.template.md alone would have let them leave
        # its coverage. The supplementary template is appended, clean and
        # corrupted alike, so the moved sentences are swept where they now sit.
        _base = exp.get("_template") or open("PAPER.template.md").read()
        findings = horizon_sweep.scan(_base + "\n\n" + open(_BC_TEMPLATE).read())
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
    if k == "population_partition":
        # Three run populations the paper quotes against one another -- every run
        # trained, the collapse family at the released architecture width, and the
        # subset the collapse rate is fitted over -- plus the table a reader is
        # invited to count. Each population is a substituted key, so no numeral
        # here can be typed; what was unasserted is that they PARTITION. Four
        # relations, all of which must hold:
        #   family + excluded          == total
        #   fitted + fitted_excluded   == family
        #   sum of the table's row counts == total, and each row's seed-id list
        #                                 is as long as its own seed count
        #   the figure's own recorded run count == family
        # The last one is why the caption and the prose cannot disagree again:
        # scripts/paper_figures.py writes the population it actually plotted.
        N = art("paper_numbers.json")
        def _i(key):
            return int(str(N[key]["value"]).replace(",", ""))
        tot = int(exp.get("_forced_total", _i(exp["total"])))
        fam, exc = _i(exp["family"]), _i(exp["excluded"])
        fit, fexc = _i(exp["fitted"]), _i(exp["fitted_excluded"])
        rows = [r for r in str(N[exp["table"]]["value"]).splitlines() if r.strip()]
        cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
        # Column order is fixed by paper_numbers.py: ... | width | seeds | seed ids.
        widths = [c[-3] for c in cells]
        counts = [int(c[-2]) for c in cells]
        ids = [len([x for x in c[-1].split(",") if x.strip()]) for c in cells]
        ok_widths = bool(cells) and all(w.isdigit() for w in widths)
        ok_rows = counts == ids
        ok = (fam + exc == tot and fit + fexc == fam
              and sum(counts) == tot and ok_widths and ok_rows)
        _figf, _figk, _figv = exp["figure_family"]
        if os.path.exists(os.path.join(R.RESULTS, _figf)):
            _plotted = art(_figf)[_figk][_figv]
            ok = ok and _plotted == fam
            _fig = f"; figure plots {_plotted}"
        else:
            _fig = "; figure artifact absent"
        return ok, (f'{exp["family"]}={fam} + {exp["excluded"]}={exc} = {fam + exc} '
                    f'vs {exp["total"]}={tot}; {exp["fitted"]}={fit} + '
                    f'{exp["fitted_excluded"]}={fexc} = {fit + fexc} vs {fam}; '
                    f'table {len(cells)} rows sum {sum(counts)}, widths '
                    f'{sorted(set(widths))}, seed-id lengths '
                    f'{"match" if ok_rows else "differ"}' + _fig)
    if k == "kind-count":
        # Three counts that must be one: what section 9 claims, what appendix D
        # enumerates, and what this file actually registers at runtime.
        N = art("paper_numbers.json")
        registered = len({c["kind"] for c in CLAIMS})
        claimed = int(exp.get("_forced", N[exp["key"]]["value"]))
        # The enumeration used to sit in appendix D. It moved to docs/BUILD_CHECKS.md
        # when appendix D was cut to a page (Session 5a). The check is RE-POINTED
        # rather than deleted or relaxed -- it still asserts that section 8's stated
        # count, the enumeration and this file's runtime registry are one number,
        # which is the whole reason it exists. A missing file fails the check.
        _bc_path = os.path.join("docs", "BUILD_CHECKS.md")
        _bc = open(_bc_path).read() if os.path.exists(_bc_path) else ""
        i = _bc.find("**The check kinds.**")
        seg = _bc[i:_bc.find("\n\n", i)] if i >= 0 else ""
        # "_" is in the class because one kind is spelled figure_reference; without
        # it that kind is enumerated in the paragraph and counted by nobody.
        enumerated = len(set(re.findall(r"\*([a-z][a-z_-]+)\*", seg)))
        ok = registered == claimed == enumerated and i >= 0
        return ok, (f'registered {registered}, the accounting claims {claimed}, '
                    f'docs/BUILD_CHECKS.md enumerates {enumerated}')
    if k == "frequency-consistency":
        # A stated frequency IS a claim about a count. "at exactly one place",
        # "in all four", "the only", "at every horizon" -- each asserts a
        # relation between a count and a total, and each was previously written
        # in words and checked by nobody. The count and the total come from the
        # artifacts; the sentence has to use wording that matches what they say.
        c_ = int(str(exp.get("_forced_count", dig(*exp["count"]))).replace(",", ""))
        t_ = int(str(dig(*exp["total"])).replace(",", ""))
        want = exp["expect"]
        got = "all" if c_ == t_ else ("none" if c_ == 0 else ("one" if c_ == 1 else "some"))
        WORDS_FOR = {
            "all": ("every", "all ", "always", "each of", "every one of them"),
            # "leads in 0 of 5" states the frequency as a numeral; that is a
            # perfectly good way to say "never" and the check must accept it.
            "none": ("no ", "never", "none", "not at any", "zero", "in 0 of", "0 of"),
            "one": ("exactly one", "the only", "one place", "a single"),
            "some": ("of the", "of its", "of them"),
        }
        win = _window(paper, exp["says"], span=exp.get("span", 200)).lower()
        said = [w for w in WORDS_FOR[want] if w in win]
        ok = got == want and bool(win) and bool(said)
        return ok, (f'{c_} of {t_} -> "{got}", text claims "{want}"'
                    + (f'; wording {said[:2]}' if said else '; NO matching wording in the window')
                    + ('' if win else '; the fragment is not in the paper'))
    if k == "restatement":
        import restatement_index
        text = (exp["_template_text"] if exp.get("_template_text")
                else open("PAPER.template.md").read())
        # B4: the moved text is scanned where it now sits (see horizon-consistency).
        text = text + "\n\n" + open(_BC_TEMPLATE).read()
        vals = art("paper_numbers.json")
        tr = restatement_index.typed_restatements(text, vals)
        _, amb = restatement_index.analyse(restatement_index.scan(text, vals), vals)
        return not (tr or amb), (
            f'{len(tr)} typed restatement(s), {len(amb)} ambiguous numeral(s)'
            + ('' if not tr else
               f'; first: {tr[0]["typed"]} in §{tr[0]["typed_section"][:24]} against '
               f'{tr[0]["key"]}={tr[0]["key_value"]}')
            + ('' if not amb else
               f'; ambiguous: {amb[0]["value"]} as {amb[0]["units"]} in '
               f'§{amb[0]["section"][:24]}'))
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
    if k == "unit-consistency":
        # Every "n_independent = N" in the prose must name its unit in the same sentence.
        # The unit is what a reader needs to compare two figures at all: 60 units of 33
        # rows and 4 units of 400 rows are both "n_independent", and the paper now carries
        # both.
        markers = exp["unit_markers"]
        bad = []
        for m in re.finditer(r"n_independent[^.]{0,200}", paper):
            seg = m.group(0)
            if not re.search(r"n_independent\s*=?\s*\*{0,2}\d", seg):
                continue
            # THE ENCLOSING PARAGRAPH, not the sentence. This follows the granularity
            # horizon-consistency already uses in this file: a calibration figure must
            # name its horizon in its own sentence, and everything else horizon-indexed
            # must name it in the enclosing paragraph. A unit is the second kind. A
            # paragraph that has said "400-step trajectories" once does not have to
            # repeat it in every cell, and requiring that would push the paper toward
            # noise rather than clarity. What the check forbids is an n_independent
            # whose unit is nowhere in the passage that states it.
            pstart = paper.rfind("\n\n", 0, m.start())
            pend = paper.find("\n\n", m.start())
            para = paper[(pstart + 2) if pstart >= 0 else 0:
                         pend if pend >= 0 else len(paper)]
            if not any(w in para for w in markers):
                bad.append(seg[:70].replace("\n", " "))
        return not bad, (f'{len(bad)} n_independent figure(s) naming no unit'
                         + (f'; first: "{bad[0]}"' if bad else ''))
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
    if k == "figure_reference":
        # Two assertions, both about numbers this document owns. Every figure
        # number the prose cites must name a figure that exists, and the count of
        # distinct numbers cited must not exceed the number of figures -- the
        # second catches the case where each reference is individually in range
        # and the set as a whole cannot be satisfied.
        # "Fig." is deliberately NOT matched: those references are the original
        # papers' figure numbers, which this document does not number.
        n_figs = exp.get("_forced_n_figures",
                         len(re.findall(r"\]\(figures/paper_fig", paper)))
        cited = sorted({int(m) for m in re.findall(r"Figure~?\s*(\d+)", paper)})
        dangling = [n for n in cited if not 1 <= n <= n_figs]
        ok = bool(cited) and not dangling and len(cited) <= n_figs
        return ok, (f'{n_figs} figures, {len(cited)} distinct numbers cited {cited}'
                    + (f'; dangling {dangling}' if dangling else ''))
    if k == "table_renders":
        # The source side is parsed with the CONVERTER's own table detector, so
        # the two cannot disagree about what counts as a table.
        import md_to_tex
        lines_ = paper.split("\n")
        src, j = [], 0
        while j < len(lines_):
            if lines_[j].startswith("|") and md_to_tex._is_table(lines_, j):
                rows = 0
                while j < len(lines_) and lines_[j].startswith("|"):
                    cs = re.split(r"(?<!\\)\|", lines_[j])[1:-1]
                    if not all(set(x.strip()) <= set("-: ") for x in cs):
                        rows += 1
                    j += 1
                src.append(rows)
            else:
                j += 1
        tex = open("PAPER.tex").read()
        ren = [len(re.findall(r"\\\\", m.group(2))) for m in re.finditer(
            r"\\begin\{(tabular|longtable)\}(.*?)\\end\{\1\}", tex, re.S)]
        bump = int(exp.get("_forced_extra_rows", 0))
        short = [(t, s, r) for t, (s, r) in enumerate(zip(src, ren)) if r < s + bump]
        ok = bool(src) and len(src) == len(ren) and not short
        return ok, (f'{len(src)} source tables, {len(ren)} rendered; source rows '
                    f'{src} vs row separators {ren}'
                    + (f'; short {short}' if short else ''))
    if k == "arena_consistency":
        E = art("evidence_summary.json")
        forms = {lab: tuple(fs) for lab, fs in E["arena_surface_forms"].items()}
        swap = bool(exp.get("_forced_arena_swap"))
        bad, conf_a, conf_n = [], 0, 0
        for r in E["rows"]:
            sec = _section_text(paper, r["section"])
            if sec is None:
                bad.append(f'{r["section"]}: no such section in the paper')
                continue
            stated_a = _stated_arenas(sec, forms)
            stated_n = _stated_nind(sec)
            arena = r["arena"]
            if swap:
                # The tightest corruption available: an arena the section does
                # not name, so an off-by-one-arena table is rejected rather than
                # only an absurd one. Corrupting the expectation and not the
                # paper keeps the self-test read-only, as every other kind does.
                other = [a for a in forms if a != arena and a not in stated_a]
                arena = (other or [a for a in forms if a != arena])[0]
            if stated_a and arena not in stated_a:
                bad.append(f'{r["section"]}: table says {arena}, section names {stated_a}')
            elif stated_a:
                conf_a += 1
            if stated_n and r["n_independent"] not in stated_n:
                bad.append(f'{r["section"]}: table says n_independent = '
                           f'{r["n_independent"]}, section states {sorted(stated_n)}')
            elif stated_n:
                conf_n += 1
        ok = bool(E["rows"]) and not bad and conf_a > 0 and conf_n > 0
        return ok, (f'{len(E["rows"])} claims; arena confirmed against its own section '
                    f'in {conf_a}, n_independent in {conf_n}'
                    + (f'; {len(bad)} mismatch(es), first: {bad[0]}' if bad else ''))
    if k == "rule-seed-scope":
        keys = re.compile(r"\{\{(?:" + exp["keys_regex"] + r")\}\}")
        trig, mark, W = re.compile(exp["trigger_regex"], re.I), re.compile(exp["marker_regex"], re.I), exp["window_lines"]
        bad, n, plant, missed_plant = [], 0, exp.get("_plant", {}), []
        for f in exp["files"]:
            L = open(f).read().split("\n")
            n0 = len(L)
            if f in plant:                         # --self-test: the old wording, appended
                L += [""] + plant[f].split("\n")
            blk, b_i = [], 0                       # paragraph index of every line
            for ln in L:
                if not ln.strip():
                    b_i += 1
                blk.append(b_i)
            for i, ln in enumerate(L):
                if not keys.search(ln):
                    continue
                if not any(trig.search(L[j]) for j in range(max(0, i - W), min(len(L), i + W + 1))):
                    continue
                n += 1
                cur = blk[i]              # this paragraph, and the next non-empty one (a table's caption sentence)
                follow = next((blk[j] for j in range(i + 1, len(L)) if blk[j] > cur and L[j].strip()), None)
                region = "\n".join(x for j, x in enumerate(L) if blk[j] == cur or blk[j] == follow)
                if not mark.search(region):
                    bad.append(f"{f}:{i + 1}")
            if f in plant and not any(b.startswith(f"{f}:") and int(b.rsplit(":", 1)[1]) > n0 for b in bad):
                missed_plant.append(f)
        if missed_plant:                           # every planted paragraph must be caught, not just one
            return True, f"planted old wording NOT caught in {missed_plant}"
        return n > 0 and not bad, (f"{n} lines quote the rule-horizon figures near 'rule'/'pre-register'; "
                                   f"{n - len(bad)} name the seed or the three-seed extension"
                                   + (f"; missing at {bad}" if bad else ""))
    if k == "overstat-reversal":
        fig, rev = re.compile(r"\{\{(?:" + exp["figure_regex"] + r")\}\}"), re.compile(exp["reversal_regex"], re.I)
        bad, n, plant, missed_plant = [], 0, exp.get("_plant", {}), []
        for f in exp["files"]:
            paras = [(p, False) for p in re.split(r"\n\s*\n", open(f).read())]
            if f in plant:                         # --self-test: the old wording, appended
                paras += [(p, True) for p in re.split(r"\n\s*\n", plant[f])]
            caught_plant = False
            for para, planted in paras:
                sents = re.split(r"(?<=[.;])\s+", para)
                if any(re.search(r"overstat", s, re.I) and fig.search(s) for s in sents):
                    n += 1
                    if not rev.search(para):
                        bad.append(f"{f}: {para.strip()[:70]!r}")
                        caught_plant |= planted
            if f in plant and not caught_plant:
                missed_plant.append(f)
        if missed_plant:
            return True, f"planted old wording NOT caught in {missed_plant}"
        return not bad, (f"{n} paragraphs pair 'overstat' with an alignment figure; "
                         f"{n - len(bad)} name the reversal" + (f"; missing in {bad}" if bad else ""))
    if k == "compute-claim":
        forb, comp, qual = (re.compile(exp[x], re.I) for x in ("forbidden_regex", "compute_regex", "qualifier_regex"))
        plant = exp.get("_plant", {})
        bad, n_front, per_region = [], 0, {}
        for f in exp["files"]:
            if not os.path.exists(f):
                bad.append(f"{f}: missing")
                continue
            txt = open(f).read() + ("\n\n" + plant["forbidden"] if f == "PAPER.md" and "forbidden" in plant else "")
            bad += [f"{f}: {m.group(0)[:60]!r}" for m in forb.finditer(txt)]
        n_forb = len(bad)
        regions = _front_matter_regions(open("PAPER.md").read())
        if "front" in plant:
            regions["abstract"] += "\n" + plant["front"]
        for name, reg in regions.items():
            assert reg.strip(), f"front-matter region {name} is empty"
            per_region[name] = 0
            for s in re.split(r"(?<=[.;])\s+", reg.replace("\n", " ")):
                if comp.search(s):
                    n_front += 1
                    per_region[name] += 1
                    if not qual.search(s):
                        bad.append(f"{name}: {s.strip()[:80]!r}")
        if plant:                                  # --self-test: each planted sentence must be among the failures
            missed = [p for p in plant.values() if not any(p.strip()[:40] in b or forb.search(p) and
                                                           any(forb.search(p).group(0)[:40] in b for b in bad) for b in bad)]
            if missed:
                return True, f"planted wording NOT caught: {[m[:50] for m in missed]}"
        return not bad and n_front > 0, (f"{n_forb} forbidden phrasings in {len(exp['files'])} rendered files; {n_front} front-matter "
                                         f"sentences name compute or longer training ({per_region}), "
                                         f"{n_front - len([b for b in bad if b.split(':')[0] in regions])} with the "
                                         f"qualifier" + (f"; failures {bad}" if bad else ""))
    if k == "alignment-arena":
        dre, sre, tre = (re.compile(exp[x], re.I) for x in ("defect_regex", "short_regex", "all_ten_regex"))
        plant = exp.get("_plant", {})
        bad, n = [], 0
        for f in exp["files"]:
            txt = open(f).read() + ("\n\n" + plant[f] if f in plant else "")
            for para in re.split(r"\n\s*\n", txt):
                for s in re.split(r"(?<=\.)\s+", para.replace("\n", " ")):
                    if dre.search(s) and sre.search(s):
                        n += 1
                        if not tre.search(para):
                            bad.append(f"{f}: {s.strip()[:80]!r}")
        if plant and not any(any(p.strip()[:40] in b.replace("\n", " ") or p.split(".")[0].strip()[:40] in b
                                 for b in bad) for p in plant.values()):
            return True, f"planted wording NOT caught: {[p[:50] for p in plant.values()]}"
        return n > 0 and not bad, (f"{n} sentences pair the alignment defect with a short-horizon cost; "
                                   f"{n - len(bad)} have the all-ten-episodes figures or words in their paragraph"
                                   + (f"; missing in {bad}" if bad else ""))
    if k == "action-response":
        plant = exp.get("_plant", {})
        bad, n = [], 0
        for f in exp["files"]:
            txt = open(f).read() + ("\n\n" + plant[f] if f in plant else "")
            # a paragraph is a blank-line block in the templates, and one A(...) call in the model card's builder
            paras = re.split(r"\n\s+A\(", txt) if f.endswith(".py") else re.split(r"\n\s*\n", txt)
            for para in paras:
                if re.search(r"\{\{stale_armA_|v\('stale_armA_", para):
                    n += 1
                    if not re.search(r"\{\{x2_|v\('x2_", para):
                        bad.append(f"{f}: {para.strip()[:70]!r}")
        if plant and not any(p.strip()[:40] in b for p in plant.values() for b in bad):
            return True, f"planted wording NOT caught: {[p[:50] for p in plant.values()]}"
        return n > 0 and not bad, (f"{n} paragraphs cite Arm A's stale-pairing figures; {n - len(bad)} carry an X2 key"
                                   + (f"; missing in {bad}" if bad else ""))
    raise ValueError(k)


# Round 3, R3 (G2, G3): round 2's wording, verbatim from the template at 8c2c903.
_OLD_ALIGN_ABSTRACT = ("Separately, the released evaluation pairs each prediction with the previous step's action, inflating "
                       "error mainly at short horizons; at the longest the cost is small and not consistent in sign.")
_OLD_ARMA_STALE = ("Our own Arm A checkpoints at {{iters_long}} iterations, trained under the causal pairing, change by "
                   "{{stale_armA_rel_h1}}% at h = 1 and {{stale_armA_rel_h368}}% at h = {{v2_diag_h}} when fed the "
                   "stale one (three-seed mean, relative-L1, held-out pair).")


# Round 3, R2 (G1): the abstract's sentence as the 4 Oct draft rendered it (commit 8c2c903), verbatim, and a
# front-matter sentence that names longer training with no qualifier, which the second half must catch.
_OLD_COMPUTE_ABSTRACT = ("On accuracy alone, two shorter histories and both longer training forecasts beat the original's "
                         "setting at our budget, the best, at 368 steps, even when that setting trains twice as long (post "
                         "hoc); it was chosen as a trade-off with training time, untested here.")
_BARE_COMPUTE_FRONT = "Trained longer, the original's setting still trails the best longer forecast on the held-out pair."


# The real wording the C25 checks exist to catch, verbatim from git history (see corruption_for).
_OLD_RULE_SCOPE_PAPER = """- **The base paper's central training claim reproduces, and reverses at one step.** Under a rule
  committed before the runs, training on the model's own rollouts beats teacher forcing, by
  {{d1_ratio}}× on relative-L1 at h = {{v2_diag_h}} over {{d1_seeds}} seeds and by
  {{d1_ratio_h100}}× at h = {{v2_deploy_h}} (§5)."""
_OLD_RULE_SCOPE_README = """Autoregressive training beats teacher forcing by a factor of **{{d1_ratio}}×** on the reference's
own relative-L1 error at the {{v2_diag_h}}-step open-loop horizon, over {{d1_seeds}} seeds on
held-out episodes ({{d1_A_mean}} against {{d1_B_mean}}), under a decision rule committed to git
before the runs that tested it existed."""
_OLD_OVERSTAT_PAPER = """predict state *t* — stale by one step. Scored correctly the released checkpoint is materially
better than its own released evaluation reports: nRMSE at h = 368 falls from {{stale_nrmse}}
under the released pairing to {{causal_nrmse}} under the causal one, so the released evaluation
overstates its own model's error by {{stale_pct}}%."""


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
    if k == "retraction_class_consistency":
        # Move one entry to the other class. That is the tightest corruption
        # available and it is the shape of the real defect: an identifier the
        # paper files under a class the ledger does not give it. Corrupting the
        # expectation -- the ledger side -- rather than the paper keeps the
        # self-test read-only, as every other kind here does.
        return {"_forced_ledger": {"S-15": "evidence"}}
    if k == "unit-consistency":
        # Remove the markers, so every n_independent in the paper reads as unit-less and
        # the check must fail. Corrupting the EXPECTATION rather than the paper keeps the
        # self-test read-only, as every other kind here does.
        return {"unit_markers": ["\x00no-such-unit-marker\x00"]}
    if k == "cross-artifact-sync":
        return {"keys": c["keys"] + ["d1_ratio"], "file": "requirements.txt"}
    if k == "abstract-budget":
        # Corrupt BOTH limbs, not just the word count. This returned
        # {"max_words": 10} and never touched max_numerals, so the numeral budget
        # -- which sits at its exact ceiling and is the limb that actually binds --
        # was never shown to be able to fail.
        return {"max_words": 10, "max_numerals": 0}
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
    if k == "population_partition":
        # Move the stated total by one. That is the tightest corruption available
        # and it is the shape of the real defect: a total that no longer equals
        # the family plus the runs excluded from it, and no longer equals what
        # the table sums to. Corrupting the expectation rather than the paper
        # keeps the self-test read-only, as every other kind here does.
        N = art("paper_numbers.json")
        return {"_forced_total": int(str(N[c["total"]]["value"]).replace(",", "")) + 1}
    if k == "kind-count":
        return {"_forced": len({x["kind"] for x in CLAIMS}) + 1}
    if k == "frequency-consistency":
        # Move the count off the frequency the sentence claims: "every" must
        # reject a count that is not the total, "none" one that is not zero.
        return {"_forced_count": 1 if c["expect"] in ("all", "none") else 0}
    if k == "restatement":
        # Plant appendix D's actual defect back into the template: a typed
        # horizon in the slot §6.8's derived extremum fills. The corruption is
        # the sentence the 24 August draft really carried, not an invented one.
        #
        # B4 moved the sentence it used to be planted in (Appendix C's list of
        # failure modes) out to docs/BUILD_CHECKS.md, which this kind does not
        # scan. The plant is re-anchored to §6.8's own statement of the same
        # extremum -- same keys, same typed replacement -- so what the self-test
        # corrupts is still a real sentence of the paper and still the real
        # defect. Tested before the change: planted there, it is caught as one
        # typed restatement of d3_worst_h.
        t = open("PAPER.template.md").read()
        planted = t.replace(
            "is {{d3_worst_q}} at h={{d3_worst_h}}, fitted on episode",
            "is aleatoric at h=128, fitted on episode", 1)
        assert planted != t, ("the restatement corruption found nothing to replace; "
                              "section 6.8's worst-cell sentence has been reworded")
        return {"_template_text": planted, "_template_is_path": False}
    if k == "scope-consistency":
        # A phrase that IS in the section, standing in for a quantifier never
        # removed.
        return {"forbid": c["forbid"] + ["we did not test"]}
    if k == "figure_reference":
        # One fewer figure than the document has, so the highest number the prose
        # cites no longer names anything. That is the tightest corruption
        # available -- the check has to reject a count that is off by one, not
        # only an absurd one. Corrupting the expectation rather than the paper
        # keeps the self-test read-only, as every other kind here does.
        return {"_forced_n_figures":
                len(re.findall(r"\]\(figures/paper_fig", open(PAPER).read())) - 1}
    if k == "table_renders":
        # One more row than the source has. A converter that renders every row
        # still cannot produce a separator for a row that is not there, so the
        # check has to reject an expectation that is off by one, not only an
        # absurd one. Corrupting the expectation keeps the self-test read-only.
        return {"_forced_extra_rows": 1}
    if k == "arena_consistency":
        # Every row's arena moved to one its own section does not name, which is
        # the defect the table would introduce if a row were copied from the
        # wrong artifact.
        return {"_forced_arena_swap": True}
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
    if k == "rule-seed-scope":
        # Plant the sentences this check was written to catch, as they really stood: contribution 2
        # before round 2's T3 (commit 9c892c8) and the README's contribution 1 before the T3 review.
        # Blanking the marker could not show that the marker itself was too loose; this can.
        return {"_plant": {"PAPER.template.md": _OLD_RULE_SCOPE_PAPER, "README.template.md": _OLD_RULE_SCOPE_README}}
    if k == "overstat-reversal":
        # Plant S-20's original sentence (section 7.2 before commit 798a362): an overstatement figure
        # with no reversal anywhere in its paragraph.
        return {"_plant": {"PAPER.template.md": _OLD_OVERSTAT_PAPER}}
    if k == "alignment-arena":
        return {"_plant": {"PAPER.template.md": _OLD_ALIGN_ABSTRACT}}
    if k == "action-response":
        return {"_plant": {"PAPER.template.md": _OLD_ARMA_STALE}}
    if k == "compute-claim":
        # Plant the 4 Oct abstract sentence (the first half must catch it) and a bare front-matter sentence naming
        # longer training (the second half must catch it); either one missed leaves the check passing, which fails.
        return {"_plant": {"forbidden": _OLD_COMPUTE_ABSTRACT, "front": _BARE_COMPUTE_FRONT}}
    raise ValueError(k)


def _surface(c, paper):
    """The text a claim is evaluated against.

    B4 moved section 8's reproducibility block and all of Appendix C into
    docs/BUILD_CHECKS.md. A claim whose pinned text went with it declares
    `surface`, and is evaluated against the paper followed by that file, so the
    claim follows its text rather than being retired or silently passing on a
    stray duplicate of its anchor elsewhere. The BUILT file is named, not the
    template: these kinds compare rendered numerals ("6/Six/six") and generated
    identifiers, which exist only after substitution. Session 5a's precedent
    (C10.x) added the template, which is right for the text-level retraction
    check and would make a numeric window vacuous.
    """
    extra = [open(f).read() for f in c.get("surface", ()) if os.path.exists(f)]
    assert len(extra) == len(c.get("surface", ())), (
        f'{c["id"]}: a declared surface is missing: {c.get("surface")}')
    return "\n\n".join([paper] + extra)


def main():
    paper = open(PAPER).read()
    rows, bad = [], 0
    for c in CLAIMS:
        ok, detail = evaluate(c, _surface(c, paper))
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

    # The self-test runs on EVERY invocation, not behind a flag. It costs five
    # seconds and it writes the `self_test` block that paper_numbers.py asserts on.
    # While it was optional, a bare run silently rewrote this artifact WITHOUT the
    # block, and a stripped copy reached git: a clean clone then died at the stage
    # that collects the paper's numbers, so the paper could not be built at all
    # from a fresh checkout. `--self-test` is still accepted and now means nothing.
    if True:
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
            ok, detail = evaluate(c, _surface(c, paper), override=corrupt)
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
