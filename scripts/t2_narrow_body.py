"""
T2 -- narrow the body's claims to what the artifacts carry.

The abstract is rewritten wholesale by T3 and is not touched here; this pass fixes
the BODY. Each edit is asserted to match exactly once, per the project's patching
rule, and the matcher is whitespace-tolerant because single-line search strings
fail on wrapped prose -- which has bitten this project repeatedly.

Five of T2's seven land here:
  1  "deployment horizon" re-anchored to the verified h=100 (V2 / X-13)
  3  the "368 of 368 forecast steps" count loses its independent-trials reading
  4  the "10 of 10 held-out cells" count gains the fitting sample size
  5  ratios quoted in prose now quote their intervals (A1)
  7  headline numbers name their metric (V3)

Item 2 ("still unexplained") and item 6 ("cannot learn how wrong") are
abstract-only and are handled by T3.
"""
import difflib
import re
import shutil
import sys

TEMPLATE = "PAPER.template.md"

# (label, old, new). `old` is matched whitespace-tolerantly.
EDITS = [

    # ---------------------------------------------------------- T2.1 horizon
    ("6.2 epistemic summary sentence: re-anchor to the method's own horizon",
     "Epistemic is {{d1n_epi_over_alea_h368}}× better than aleatoric at the deployment "
     "horizon and still wrong by **{{d1n_epi_ratio_h1}}×** at one step and "
     "**{{d1n_epi_ratio_h368}}×** at the deployment horizon, with ±1σ coverage of "
     "{{d1n_epi_cov1_h368}}% where a calibrated Gaussian gives 68.3%.",

     "Epistemic is {{d1n_epi_over_alea_h368}}× better than aleatoric and still wrong by "
     "**{{d1n_epi_ratio_h1}}×** at one step and **{{d1n_epi_ratio_h100}}× "
     "[{{d1n_epi_ratio_ci_h100}}]** at h = {{v2_deploy_h}}, the method's own imagination "
     "rollout length, with ±1σ coverage of {{d1n_epi_cov1_h100}}% "
     "[{{d1n_epi_cov1_ci_h100}}] where a calibrated Gaussian gives "
     "{{v3_cov_nominal1}}%. At the open-loop diagnostic horizon of "
     "h = {{v2_diag_h}} it is {{d1n_epi_ratio_h368}}× "
     "[{{d1n_epi_ratio_ci_h368}}] with {{d1n_epi_cov1_h368}}% coverage — barely "
     "different, which is why the re-anchoring changes the reading and not the "
     "conclusion."),

    ("6.2 ens5 comparison: re-anchor",
     "Our arms are **better calibrated than the released checkpoint and fail the same "
     "way**: {{e5_ratio_h368}}× overconfident at the deployment horizon against its "
     "{{d1n_epi_ratio_h368}}×, with {{e5_cov1_h368}}% coverage where a calibrated "
     "Gaussian gives 68.3%.",

     "Our arms are **better calibrated than the released checkpoint and fail the same "
     "way**: {{e5_ratio_h100}}× overconfident at h = {{v2_deploy_h}} against its "
     "{{d1n_epi_ratio_h100}}×, with {{e5_cov1_h100}}% coverage where a calibrated "
     "Gaussian gives {{v3_cov_nominal1}}%. §6.4 establishes that the two are the same "
     "architecture in the respect that matters here, so this is a comparison of like "
     "with like."),

    ("11 broader impact: re-anchor",
     "at the\ndeployment horizon the released checkpoint's ensemble disagreement is\n"
     "{{d1n_epi_ratio_h368}}× smaller than the realised error, giving "
     "{{d1n_epi_cov1_h368}}% coverage where 68.3% is expected.",

     "at the horizon the method itself rolls out over — h = {{v2_deploy_h}} — the "
     "released checkpoint's ensemble disagreement is {{d1n_epi_ratio_h100}}× smaller "
     "than the realised error, giving {{d1n_epi_cov1_h100}}% coverage where "
     "{{v3_cov_nominal1}}% is expected."),

    ("12 limitations: re-anchor the cost caveat",
     "We show that the penalty the follow-up applies is miscalibrated as a scale — "
     "{{d1n_epi_ratio_h368}}× overconfident at the deployment horizon — but",

     "We show that the penalty the follow-up applies is miscalibrated as a scale — "
     "{{d1n_epi_ratio_h100}}× overconfident at h = {{v2_deploy_h}}, the horizon its own "
     "imagination rollouts run to — but"),

    ("6 opening: name the horizon convention once",
     "training it with teacher forcing, at deployment horizons.",
     "training it with teacher forcing, at the horizons the method deploys at."),

    # ------------------------------------------------- T2.3 dependent counts
    ("6.7 within-step control: the count is not 368 independent trials",
     "positive at **{{d2r_win_pos}} of {{d2r_win_n}}** forecast steps with a median of "
     "{{d2r_win_med}}. The weakest figure across all {{d2r_ncontrols}} controls is "
     "{{d2r_weakest}}. Disagreement is not re-encoding the clock: at a fixed depth it "
     "still knows which rollouts are going wrong.",

     "positive at {{d2r_win_pos}} of {{d2r_win_n}} forecast steps with a median of "
     "{{d2r_win_med}}.[^stepcount] The weakest figure across all {{d2r_ncontrols}} "
     "controls is {{d2r_weakest}}. Disagreement is not re-encoding the clock: at a fixed "
     "depth it still knows which rollouts are going wrong.\n\n"
     "[^stepcount]: Adjacent forecast steps on the same {{a2_nind}} trajectories are "
     "heavily dependent — structurally the same problem §6.6 spends a page correcting "
     "for the 45 coupled state dimensions. The count is descriptive; the interval "
     "{{d2r_win_ci}} is the statistic, and no P-value attaches to "
     "{{d2r_win_pos}}/{{d2r_win_n}}."),

    ("10 lessons: drop the raw step count",
     "That is a real signal, not a re-encoding of how far ahead you are looking: holding "
     "forecast depth exactly constant it still correlates {{d2r_win}} with error, at "
     "{{d2r_win_pos}} of {{d2r_win_n}} steps (§6.7).",

     "That is a real signal, not a re-encoding of how far ahead you are looking — and "
     "not merely a report of which episode is hard: with both the forecast depth and "
     "the rollout held constant it still correlates {{a2_rdd}} {{a2_rdd_ci}} with error "
     "(§6.7)."),

    # -------------------------------------------------- T2.4 the 10-of-10 cells
    ("6.8 per-horizon table: state the fitting sample size and the third caution",
     "Two cautions a reader should apply. The per-horizon scalar has five free "
     "parameters against the constant one's one, so it *must* fit better in sample — "
     "only the held-out column above is evidence, and that is the column reported. And "
     "the correction is a calibration patch, not a fix:",

     "Three cautions a reader should apply. The per-horizon scalar has one free "
     "parameter per horizon against the constant one's one, so it *must* fit better in "
     "sample — only the held-out column above is evidence, and that is the column "
     "reported. **And the held-out column is thinner than its count suggests:** the "
     "{{d3_epi_cells}} cells are {{d3_nhoriz}} horizons × two fold directions on the "
     "same {{d3_nind_tot}} trajectories, and each multiplier is fitted on "
     "n_independent = {{d3_nind_fit}} and scored on the other {{d3_nind_fit}}. They are "
     "not {{d3_epi_cells}} independent successes and no P-value attaches to the count; "
     "it is reported so a reader can see how thin the evidence is, alongside a result "
     "we believe. And the correction is a calibration patch, not a fix:"),

    # ------------------------------------------------- T2.5 intervals in prose
    ("6.2 four-model table: quote the intervals",
     "| model | mean \\|error\\| / mean σ, whole 368-step rollout | coverage at ±1σ, h=1 "
     "| coverage at ±1σ, h=368 |\n|---|---|---|---|\n"
     "| faithful Arm A (sampled MSE) | {{cal_faithA_ratio}}× | {{cal_faithA_cov1}}% | "
     "{{cal_faithA_cov368}}% |\n"
     "| corrected Arm A (`gaussian_nll`) | {{cal_nll_ratio}}× | {{cal_nll_cov1}}% | "
     "{{cal_nll_cov368}}% |\n"
     "| teacher-forced Arm B | {{cal_armB_ratio}}× | {{cal_armB_cov1}}% | "
     "{{cal_armB_cov368}}% |\n"
     "| released checkpoint | {{cal_rel_ratio}}× | {{cal_rel_cov1}}% | "
     "{{cal_rel_cov368}}% |",

     "| model | mean \\|error\\| / mean σ, whole {{v2_diag_h}}-step rollout | coverage at "
     "±1σ, h=1 | coverage at ±1σ, h={{v2_deploy_h}} |\n|---|---|---|---|\n"
     "| faithful Arm A (sampled MSE) | {{cal_faithA_ratio}}× "
     "[{{cal_faithA_ratio_ci}}] | {{cal_faithA_cov1}}% [{{cal_faithA_cov1_ci}}] | "
     "{{cal_faithA_cov100}}% [{{cal_faithA_cov100_ci}}] |\n"
     "| corrected Arm A (`gaussian_nll`) | {{cal_nll_ratio}}× [{{cal_nll_ratio_ci}}] | "
     "{{cal_nll_cov1}}% [{{cal_nll_cov1_ci}}] | {{cal_nll_cov100}}% "
     "[{{cal_nll_cov100_ci}}] |\n"
     "| teacher-forced Arm B | {{cal_armB_ratio}}× [{{cal_armB_ratio_ci}}] | "
     "{{cal_armB_cov1}}% [{{cal_armB_cov1_ci}}] | {{cal_armB_cov100}}% "
     "[{{cal_armB_cov100_ci}}] |\n"
     "| released checkpoint | {{cal_rel_ratio}}× [{{cal_rel_ratio_ci}}] | "
     "{{cal_rel_cov1}}% [{{cal_rel_cov1_ci}}] | {{cal_rel_cov100}}% "
     "[{{cal_rel_cov100_ci}}] |\n\n"
     "*Every cell carries a 95% interval from a cluster bootstrap over whole "
     "trajectories, n_independent = {{b2_nind}}; where three seeds contribute, seeds are "
     "pooled inside each draw rather than resampled, because seeds are not trajectories "
     "(§9). At n_independent = {{b2_nind}} the bootstrap has {{c3_resamples}} distinct "
     "resamples and the intervals are quantised at that resolution.*"),

    ("6.2 released-checkpoint note: name the metric and the horizon",
     "*A note on the released checkpoint's row, so the next table does not read as a "
     "contradiction.* Its {{cal_rel_ratio}}× is measured on those same {{b2_nind}} "
     "trajectories, for comparability with the three arms beside it. The released "
     "checkpoint trained on all ten episodes, so its own best-sampled figure is the "
     "{{d1n_alea_ratio_h368}}× below, at n_independent = {{d1n_nind}}.",

     "*A note on the released checkpoint's row, so the next table does not read as a "
     "contradiction.* Its {{cal_rel_ratio}}× is measured on those same {{b2_nind}} "
     "trajectories, for comparability with the three arms beside it. The released "
     "checkpoint trained on all ten episodes, so its own best-sampled figure is the "
     "{{d1n_alea_ratio_h100}}× below, at n_independent = {{d1n_nind}}."),
]


def patch(text, old, new, label):
    """Whitespace-tolerant single-occurrence replacement."""
    pat = re.compile(r"[\s>]+".join(re.escape(w) for w in old.split()))
    hits = list(pat.finditer(text))
    assert len(hits) == 1, (
        f"[{label}] matched {len(hits)} times, expected 1\n"
        f"  first 90 chars of pattern: {old[:90]!r}")
    return text[:hits[0].start()] + new + text[hits[0].end():]


def main():
    write = "--write" in sys.argv
    original = open(TEMPLATE).read()
    text = original
    for label, old, new in EDITS:
        text = patch(text, old, new, label)
        print(f"  ok  {label}")
    print(f"\n  {len(EDITS)} edits matched exactly once each")
    if not write:
        print("  DRY RUN — re-run with --write")
        return
    shutil.copy(TEMPLATE, TEMPLATE + ".t2bak")
    open(TEMPLATE, "w").write(text)
    d = list(difflib.unified_diff(original.splitlines(), text.splitlines(),
                                  "before", "after", lineterm="", n=0))
    print(f"  wrote {TEMPLATE} ({len(d)} diff lines)")


if __name__ == "__main__":
    main()
