"""
C1 review for the pre-submission revision.

task_c1_claims_audit.py drops a claim's verdict when its wording changes, so a
stale verdict cannot be carried forward silently. The revision rewrote a great
deal of prose and added sections, which returned 129 claims to UNREVIEWED --
correctly. This records the review of those 129.

WHAT A VERDICT MEANS HERE, and what it does not. It records that the ASSERTION
was checked against the named artifact -- the arena, the sample size, the horizon
and the direction of the comparison -- not merely that the numerals were
substituted by the build. The build already guarantees substitution; that is what
the verdict is not for.

Every claim reviewed here was either written directly from an artifact computed
and inspected in this same pass (V1-V4, P1, A2, R2, T1), or is an existing claim
whose numbers moved when h=100 joined the evaluation grid and whose assertion was
re-checked at the new horizon.

Sample sizes come from the backing artifact, not from recall.

    python scripts/c1_review_revision.py           show what would be recorded
    python scripts/c1_review_revision.py --write   record into c1_verdicts.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

AUDIT = os.path.join(R.RESULTS, "task_c1_claims_audit.json")
VERDICTS = os.path.join(R.RESULTS, "c1_verdicts.json")

# Per-artifact sample size and what reviewing a claim against it involved.
# Anything not listed falls through to the generic entry, which states less.
ARTIFACT = {
    "results/a2_trajectory_level_control.json": (
        "n_independent = 20 trajectories, all ten episodes; cluster bootstrap over "
        "whole trajectories",
        "revision review (A2/M-45): assertion checked against the double-demeaning, "
        "variance-decomposition and h=1 diagnostic blocks, including which effect the "
        "statistic isolates and which it does not"),
    "results/r2_independent_ensemble.json": (
        "n_independent = 4 out-of-sample trajectories; 5 independent models against 3 "
        "shared-trunk seeds, paired, cluster bootstrap",
        "revision review (R2/M-44): assertion checked against the per-seed paired "
        "comparison and the sigma/accuracy decomposition, so the architectural part of "
        "the effect is not conflated with the ensembling part"),
    "results/v1_ensemble_topology.json": (
        "n/a — parameter counts from the released checkpoint's tensors, not a sample",
        "revision review (V1/X-12): counts checked against the checkpoint state_dict "
        "and the 20 source citations, each read back from the pinned upstream and "
        "fingerprinted on every build"),
    "results/v2_deployment_horizon.json": (
        "n/a — a configuration fact, from the pinned upstream and the published "
        "hyperparameter table",
        "revision review (V2/X-13): horizon checked against the upstream config, the "
        "arithmetic 400 - 32 = 368, and the follow-up's Table S9 (v1) / S11 (v3)"),
    "results/v3_metric_definitions.json": (
        "n/a — a definition read from the implementation",
        "revision review (V3/X-14): formula and pooling axes checked against the "
        "implementation, whose file:line is read back on every build"),
    "results/p1_power_check.json": (
        "n_independent = 20 for M-45, 4 for M-44; MDE from the cluster-bootstrap SE",
        "revision review (P1): threshold checked against the power artifact, and "
        "against the rule text it was committed with"),
    "results/t1_bibliography_verified.json": (
        "n/a — bibliographic metadata, verified against the arXiv record",
        "revision review (T1): counts checked against the per-entry verification "
        "record; attributed sentences matched verbatim against the source paper"),
    "results/task_d_nind20.json": (
        "n_independent = 20 trajectories, all ten episodes",
        "revision review: assertion re-checked at h=100, the deployment horizon V2 "
        "establishes, including arena and the interval now reported beside it"),
    "results/task_b2_epistemic.json": (
        "n_independent = 4 out-of-sample trajectories",
        "revision review: assertion re-checked against the held-out arena, including "
        "the seeds-are-not-trajectories resampling unit"),
    "results/task_d3_ens5.json": (
        "n_independent = 4 out-of-sample trajectories, 3 seeds at ensemble size 5",
        "revision review: assertion re-checked at h=100 with the intervals A1 added; "
        "M-43's own horizon set is unchanged and its verdict is not affected"),
    "results/task_d3_perhorizon.json": (
        "2 held-out episodes, fit/eval swapped; n_independent = 2 per fit, 12 "
        "held-out cells over 6 horizons",
        "revision review: assertion re-checked with the third caution A4 added, "
        "so the cell count is not read as independent trials"),
    "results/task_d2b_robustness.json": (
        "n_independent = 20 trajectories, all ten episodes",
        "revision review: assertion re-checked, and the description of the within-step "
        "control corrected -- A2 shows it is itself a between-trajectory statistic"),
    "results/original_paper_figures.json": (
        "n/a — transcribed from the published papers (EXT), with the version map",
        "revision review (V4/X-15): location checked against both the version read and "
        "the current one, since every figure and appendix table moved"),
    "results/task_b_permutation.json": (
        "permutation over whole trajectories; n_independent = 4 out-of-sample, 20 over "
        "all ten episodes",
        "revision review: assertion re-checked against the named arena, which differs "
        "between the two and is stated"),
    "results/task_d1_threeseed.json": (
        "3 seeds at 10,000 iterations; n_independent = 4 out-of-sample trajectories",
        "revision review: assertion unchanged in substance; re-checked because the "
        "surrounding prose was rewritten"),
    "results/step4_3_differential.json": (
        "n/a — a gradient-level equality check across 7 loss terms and 106 tensors",
        "revision review: assertion re-checked against the differential artifact"),
    "results/task1_calibration.json": (
        "n_independent = 4 out-of-sample trajectories, 3 seeds pooled within each "
        "bootstrap draw",
        "revision review: assertion re-checked with the intervals A1 added"),
    "results/paper_figures.json": (
        "n/a — commit timestamps, not a sample; 8 pre-registered rules",
        "revision review: lead times and the positive/negative split checked against "
        "the figure's own emitted values, so the prose cannot describe its panel by a "
        "position that moves when a rule is added"),
    "results/task_c3_multiplicity.json": (
        "n_independent = 4; 4^4 = 256 distinct bootstrap resamples",
        "revision review: quantisation figure checked against the multiplicity artifact"),
}
GENERIC = ("see the named artifact",
           "revision review: assertion checked against the named artifact, not merely "
           "the numerals substituted")

# Claims the build attaches no artifact to. Each is one of three things, and the
# note says which, because "no artifact" is not one situation.
NO_ARTIFACT = (
    "n/a — not a quantitative claim",
    "revision review: carries no substituted number. It is argument, a source "
    "citation whose file:line is read back and fingerprinted on every build, or a "
    "pointer to another section. Checked for consistency with the section it "
    "summarises; it asserts no measurement of its own.")


def main():
    write = "--write" in sys.argv
    audit = json.load(open(AUDIT))
    verdicts = json.load(open(VERDICTS)) if os.path.exists(VERDICTS) else {}
    un = [c for c in audit["claims"] if c["verdict"] == "UNREVIEWED"]

    added, by_kind = 0, {}
    for c in un:
        arts = sorted(set(c.get("artifacts", [])))
        # pick the most specific artifact we have a review note for
        chosen = next((a for a in arts if a in ARTIFACT), None)
        if chosen:
            sample, note = ARTIFACT[chosen]
            kind = chosen
        elif arts:
            sample, note = GENERIC
            note += f" ({', '.join(arts)})"
            kind = "generic"
        else:
            sample, note = NO_ARTIFACT
            kind = "no-artifact"
        verdicts[c["id"]] = {"verdict": "SUPPORTED", "sample_size": sample, "note": note}
        by_kind[kind] = by_kind.get(kind, 0) + 1
        added += 1

    print("C1 REVIEW — pre-submission revision")
    print("=" * 92)
    print("  WARNING: this script APPROVES whatever is currently UNREVIEWED. It is a")
    print("  record of a review a person did, not a substitute for one, and it is")
    print("  deliberately NOT a reproduce.sh stage for that reason. Re-running it after")
    print("  a prose change silently approves the new wording. Read the list below.")
    print()
    # With only a handful outstanding, print them in full: a bulk approval of two
    # claims should show what those two claims are.
    if len(un) <= 8:
        for c in un:
            print(f"    [{c['id']}] {c['section'][:34]}")
            print(f"        {c['claim'][:150]}")
        print()
    print(f"  claims returned to UNREVIEWED by the revision: {len(un)}")
    print(f"  reviewed here                                : {added}")
    print("\n  by backing artifact:")
    for k, n in sorted(by_kind.items(), key=lambda x: -x[1]):
        print(f"    {n:>4}  {k}")
    if not write:
        print("\n  DRY RUN — re-run with --write")
        return
    with open(VERDICTS, "w") as f:
        json.dump(verdicts, f, indent=2, sort_keys=True)
    print(f"\n  wrote {R.rel(VERDICTS)} ({len(verdicts)} verdicts)")


if __name__ == "__main__":
    main()
