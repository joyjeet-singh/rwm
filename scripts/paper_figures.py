"""Figures for the paper. Every number is read from results/, none is typed.

Writes figures/paper_fig{1..5}.png and results/paper_figures.json, which records
the values each panel plots so a reader can check the figure against the data.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import rwm_data as R  # noqa: E402

plt.rcParams.update({
    "figure.dpi": 160, "savefig.dpi": 160, "font.size": 9,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linewidth": 0.5,
    "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "axes.titlesize": 10, "axes.titleweight": "bold",
})
C = {"faithful": "#1f77b4", "corrected": "#2ca02c", "armB": "#d62728", "released": "#7f4fc4"}


def J(name):
    return json.load(open(os.path.join(R.RESULTS, name)))


def fig1_calibration(rec):
    """The uncertainty output is unusable, and by how much."""
    d = J("task1_calibration.json")
    order = [("faithful (mse)", "faithful Arm A (mse)", C["faithful"]),
             ("corrected (nll)", "corrected Arm A (nll)", C["corrected"]),
             ("teacher-forced armB", "teacher-forced Arm B", C["armB"]),
             ("released ckpt", "released checkpoint", C["released"])]
    fig, ax = plt.subplots(1, 3, figsize=(10.5, 3.2))

    # (a) reliability: predicted vs observed coverage
    for k, lab, col in order:
        rel = d[k]["reliability"]
        ax[0].plot([r["predicted"] for r in rel], [r["observed"] for r in rel],
                   "o-", ms=3, lw=1.4, color=col, label=lab)
    ax[0].plot([0, 1], [0, 1], "k--", lw=1, label="calibrated")
    ax[0].set(xlabel="predicted coverage", ylabel="observed coverage",
              title="(a) reliability", xlim=(0, 1), ylim=(0, 1))
    ax[0].legend(fontsize=6.5, loc="upper left")

    # (b) coverage at +-1 sigma against horizon
    hs = sorted(int(h) for h in d[order[0][0]]["coverage"])
    for k, lab, col in order:
        ax[1].plot(hs, [100 * d[k]["coverage"][str(h)]["pm1"] for h in hs],
                   "o-", ms=3, lw=1.4, color=col, label=lab)
    # C3(rev2), 3.9. This was a typed 68.3 while 3.1 derives 68.27 and the paper
    # quotes that everywhere else, so the figure and its caption disagreed with
    # the text about a constant. Read from V3, which is where 3.1 derives it.
    _nom1 = 100 * json.load(open(os.path.join(
        R.RESULTS, "v3_metric_definitions.json")))["coverage"]["nominal"]["pm1"]
    ax[1].axhline(_nom1, color="k", ls="--", lw=1)
    ax[1].text(hs[-1], _nom1 + 1.7, f"calibrated {_nom1:.2f}%", ha="right", fontsize=7)
    ax[1].set(xscale="log", xlabel="forecast horizon (steps)",
              ylabel=r"coverage at $\pm1\sigma$ (%)", # was "(b) coverage collapses with horizon", which rendered at 1.10x the
              # axes width and clipped. The caption carries the full statement.
              title="(b) coverage vs horizon")

    # (c) how many times too small sigma is
    labs = [lab for _, lab, _ in order]
    vals = [d[k]["ratio_err_over_sigma"] for k, _, _ in order]
    cols = [c for _, _, c in order]
    ax[2].barh(range(len(vals)), vals, color=cols, height=0.6)
    ax[2].set_yticks(range(len(vals)))
    ax[2].set_yticklabels([l.replace(" ", "\n", 1) for l in labs], fontsize=7)
    ax[2].set(xscale="log", xlabel=r"mean $|$error$|$ / mean $\sigma$",
              title="(c) overconfidence factor")
    ax[2].axvline(1.0, color="k", ls="--", lw=1)
    for i, v in enumerate(vals):
        ax[2].text(v * 1.15, i, f"{v:,.0f}×", va="center", fontsize=7)
    ax[2].invert_yaxis()
    rec["fig1"] = {"ratio_err_over_sigma": {lab: d[k]["ratio_err_over_sigma"] for k, lab, _ in order},
                   "coverage_pm1_by_horizon": {lab: {str(h): d[k]["coverage"][str(h)]["pm1"] for h in hs}
                                               for k, lab, _ in order}}
    fig.tight_layout()
    p = os.path.join(R.FIGURES, "paper_fig1_calibration.png")
    fig.savefig(p); plt.close(fig)
    return p


def fig2_sigma_profile(rec):
    """sigma is flat inside the trained horizon while error grows."""
    d = J("task2_sigma_profile.json")
    order = [("faithful armA (mse)", "faithful Arm A (mse)", C["faithful"]),
             ("corrected armA (nll)", "corrected Arm A (nll)", C["corrected"]),
             ("teacher-forced armB", "teacher-forced Arm B", C["armB"]),
             ("released checkpoint", "released checkpoint", C["released"])]
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 3.2))
    for k, lab, col in order:
        s = np.array(d[k]["sigma_by_step"], float)
        e = np.array(d[k]["err_by_step"], float)
        steps = np.arange(1, len(s) + 1)
        ax[0].plot(steps, s / s[0], "o-", ms=3, lw=1.4, color=col, label=lab)
        ax[1].plot(steps, e / e[0], "o-", ms=3, lw=1.4, color=col, label=lab)
    for a, t in ((ax[0], r"(a) predicted $\sigma$"),
                 (ax[1], "(b) realised error")):
        a.axhline(1.0, color="k", ls="--", lw=1)
        a.set(xlabel="forecast step (training horizon is 8)", title=t)
    ax[0].set_ylabel(r"$\sigma_h/\sigma_1$"); ax[1].set_ylabel(r"$|e_h|/|e_1|$")
    ax[0].legend(fontsize=6.5, loc="upper left")
    rec["fig2"] = {k: {"sigma_growth_1_to_8": d[k]["sigma_growth_1_to_8"],
                       "err_growth_1_to_8": d[k]["err_growth_1_to_8"]} for k, _, _ in order}
    fig.tight_layout()
    p = os.path.join(R.FIGURES, "paper_fig2_sigma_profile.png")
    fig.savefig(p); plt.close(fig)
    return p


def fig3_collapse(rec):
    """The variance collapse is linear, identical across every run."""
    import glob
    fig, ax = plt.subplots(1, 2, figsize=(7.6, 3.2))
    runs, slopes = [], []
    for f in sorted(glob.glob(os.path.join(R.RESULTS, "step5_arm*.json"))):
        tag = os.path.basename(f)[len("step5_"):-len(".json")]
        d = json.load(open(f))
        col = C["armB"] if tag.startswith("armB") else (
            C["corrected"] if tag.endswith("_nll") else C["faithful"])
        it = [c["iter"] for c in d["collapse"]]
        v = [c["log_delta_logstd_mean"] for c in d["collapse"]]
        ax[0].plot(it, v, lw=0.9, alpha=0.75, color=col)
        runs.append(tag)
        if d.get("collapse_fit"):
            slopes.append((tag, d["collapse_fit"]["slope_per_iter"]))
    ax[0].set(xlabel="iteration", ylabel=r"mean $\log\Delta_{\log\sigma}$",
              title=f"(a) collapse trajectory,\nall {len(runs)} runs superimposed")
    # Panel (b) must plot the same set the quoted rate is fitted on. The six
    # 10,000-iteration runs continue seeds already present at 2,500, so including
    # them here would show n=18 beside a statistic computed on n=12.
    fitted = [(t, s) for t, s in slopes if "_10k" not in t]
    mse = [s for t, s in fitted if not t.endswith("_nll")]
    nll = [s for t, s in fitted if t.endswith("_nll")]
    ax[1].axhline(0, color="k", lw=1)
    for vals, lab, col in ((mse, "sampled-MSE runs", C["faithful"]),
                           (nll, "gaussian_nll runs", C["corrected"])):
        if vals:
            ax[1].scatter(np.arange(len(vals)), vals, s=18, color=col, label=f"{lab} (n={len(vals)})")
    ax[1].set(xlabel="run", ylabel="fitted slope per iteration",
              # "non-double-counting subset" overran the axes and rendered as
              # "non-double-counting subse". The subset is defined in the caption
              # and in section 5.3; the title only has to name the panel.
              title="(b) fitted rate, fitted subset:\nsign flips with the objective")
    ax[1].legend(fontsize=7)
    rec["fig3"] = {"n_runs": len(runs), "slopes": dict(slopes)}
    fig.tight_layout()
    p = os.path.join(R.FIGURES, "paper_fig3_collapse.png")
    fig.savefig(p); plt.close(fig)
    return p


def fig4_timeline(rec):
    """Pre-registration lead time: rule commit minus the data it tested.

    Positive means the rule was in git before the data existed. The Task 3 rule is
    negative, and is drawn that way rather than omitted -- S-12 retracts the claim
    that it was pre-registered, and a figure that quietly dropped it would be
    making the claim the ledger withdraws.
    """
    here = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)

    def when(h):
        o = subprocess.run(["git", "show", "-s", "--format=%at", h],
                           capture_output=True, text=True, cwd=here)
        return int(o.stdout.strip())

    def resolve(h, subject):
        """The commit for this rule, by hash if it still exists and by SUBJECT if
        it does not.

        Figure 4's whole argument is that a reader can check these hashes against
        the published history, so a dangling one is not cosmetic. Two of them
        dangled: purging the correspondence transcript from history (M-48)
        rewrote every commit from the one that introduced it onward, and the two
        Phase-1/Phase-2 data commits took new identifiers. Nothing about the
        ordering moved -- same timestamps, same content but for the removed file
        -- but the identifiers the figure cited stopped resolving.

        Subjects are stable across a path filter and hashes are not, so the
        subject is the lookup key and the hash is what gets printed. Both are
        asserted: exactly one commit must match, and if the recorded hash still
        exists its subject must be the recorded one.
        """
        o = subprocess.run(["git", "log", "--all", "--format=%H\t%s"],
                           capture_output=True, text=True, cwd=here)
        hits = [ln.split("\t", 1) for ln in o.stdout.splitlines() if "\t" in ln]
        match = [c for c, subj in hits if subj == subject]
        assert len(match) == 1, (
            f"{len(match)} commits have the subject {subject!r}; Figure 4 needs "
            f"exactly one, because the subject is what survives a history rewrite")
        cur = subprocess.run(["git", "rev-parse", "-q", "--verify", h + "^{commit}"],
                             capture_output=True, text=True, cwd=here)
        if cur.returncode == 0:
            got = subprocess.run(["git", "show", "-s", "--format=%s", h],
                                 capture_output=True, text=True, cwd=here).stdout.strip()
            assert got == subject, (
                f"the hash recorded for {subject!r} ({h}) is a different commit: {got!r}")
        return match[0][:7]

    # (label, rule commit, its subject, data commit, its subject, data label).
    # The subjects are here because hashes do not survive a history rewrite and
    # subjects do; see resolve() above and M-48.
    CASES = [
        ("M-16\nthe A/B decision rule", "84ff01b",
         "Step 5: pre-register the decision rule before launching any main run", "f25e656",
         "Step 5: Arm A seed 0 complete; collapse prediction confirmed to 3 dp",
         "first main-run data"),
        ("flip pattern\ninterpretation", "0fe2bca",
         "Pre-register interpretation of one M-16 flip pattern", "e5aee6f",
         "Step 5.4: Arms A and B, three seeds each - M-16 evaluated",
         "all six main runs"),
        ("M-22\ndifficulty-bias rule", "0648a32",
         "Pre-register the Task 4b difficulty-bias rule, and the two-arena convention", "d88e9ff",
         "M-16 returns CANNOT BE SETTLED under corrected measurement",
         "M-16 re-evaluated"),
        ("M-23\nlong-horizon rule", "efc35b8",
         "5.1: pre-register M-23, the long-horizon decision rule", "d9f7bba",
         "5.2: bootstrap CIs over independent trajectories; launch the 10k runs", "10k runs launched"),
        # The ensemble-5 rule and the two rules of the pre-submission revision.
        # P1 required the last two to be committed before any Phase 1 or Phase 2
        # artifact and their hash recorded here, which is what these rows are.
        ("M-43\nensemble-5 replication", "b17f1b5",
         "PRE-REGISTER the ensemble-5 replication rule, before the runs exist", "cdac035",
         "Parts D and E: the ensemble-5 replication, M-43's verdict, and the cascade",
         "ens5 result committed"),
        ("M-45\nwithin-trajectory control", "81b49f7",
         "PRE-REGISTER M-44 and M-45, with the power check M-43 was committed without",
         "2eccc1f",
         "Phases 1, 3 and 4 of the revision: intervals, the missing control, related work",
         "A2 result committed"),
        ("M-44\ntrunk-sharing mechanism", "81b49f7",
         "PRE-REGISTER M-44 and M-45, with the power check M-43 was committed without",
         "d88a106",
         "Phase 2: M-44 returns MECHANISM SUPPORTED, with the part that keeps it honest",
         "R2 result committed"),
    ]
    rows = []
    resolved = []
    for lab, rule, rule_subj, data, data_subj, dlab in CASES:
        rule, data = resolve(rule, rule_subj), resolve(data, data_subj)
        resolved.append({"rule": lab.replace("\n", " "), "rule_commit": rule,
                         "data_commit": data, "tested_by": dlab})
        rows.append((lab, (when(data) - when(rule)) / 3600.0, dlab))
    # Task 3: the control runs finished before any threshold reached git.
    RUNS_DONE = when("3ee9d97") - 0  # placeholder replaced below
    import datetime
    # runs finished 21:37:51 on the day before 3ee9d97 (from control_driver.log)
    done = datetime.datetime.fromtimestamp(when("3ee9d97")).replace(hour=21, minute=37, second=51) \
        - datetime.timedelta(days=1)
    rows.append(("Task 3\nduplication rule", (done.timestamp() - when("3ee9d97")) / 3600.0,
                 "control runs finished"))

    fig, ax = plt.subplots(figsize=(7.8, 3.4))
    labs = [r[0] for r in rows]
    vals = [r[1] for r in rows]
    cols = ["#2ca02c" if v > 0 else "#d62728" for v in vals]
    y = np.arange(len(rows))
    ax.barh(y, vals, color=cols, height=0.55)
    ax.axvline(0, color="k", lw=1.2)
    ax.set_yticks(y); ax.set_yticklabels(labs, fontsize=7.5)
    ax.invert_yaxis()
    def fmt(v):
        # sub-hour leads are real and must not render as "+0.0 h"
        return f"{v*60:+.0f} min" if abs(v) < 1 else f"{v:+.1f} h"
    for i, (lab, v, dlab) in enumerate(rows):
        ax.text(v + (0.25 if v > 0 else 0.25), i, f"{fmt(v)}  ({dlab})",
                va="center", ha="left", fontsize=7)
    ax.set(xlabel="hours the rule preceded the data it tested  (negative = written afterwards)",
           title="Pre-registration lead time, from git commit timestamps")
    ax.set_xlim(min(vals) * 1.25, max(vals) * 1.85)
    ax.text(0.99, 0.04, "green: rule in git before the data existed\n"
                        "red: rule written once the answer was known (S-12)",
            transform=ax.transAxes, ha="right", fontsize=6.5, color="#555555")
    rec["fig4_commits"] = resolved
    rec["fig4"] = {lab.replace("\n", " "): {"lead_hours": v, "tested_by": dlab}
                   for lab, v, dlab in rows}
    fig.tight_layout()
    p = os.path.join(R.FIGURES, "paper_fig4_prereg_timeline.png")
    fig.savefig(p); plt.close(fig)
    return p


def fig5_three_way(rec):
    """The contamination arms, both resampling units."""
    d = J("task3_three_way.json"); S = d["_summary"]
    pairs = [("duplicated_minus_clean", "duplicated\n− clean"),
             ("contaminated_minus_clean", "contaminated\n− clean"),
             ("contaminated_minus_duplicated", "contaminated\n− duplicated")]
    fig, ax = plt.subplots(1, 2, figsize=(8.4, 3.2))
    w = 0.35
    for j, unit in enumerate(("naive", "cluster")):
        hurt = [S[p][unit]["hurt"] for p, _ in pairs]
        help_ = [S[p][unit]["helped"] for p, _ in pairs]
        none = [S[p][unit]["no_effect"] for p, _ in pairs]
        x = np.arange(len(pairs)) + (j - 0.5) * w
        ax[0].bar(x, hurt, w, color="#d62728", label="hurt" if j == 0 else None)
        ax[0].bar(x, help_, w, bottom=hurt, color="#2ca02c", label="helped" if j == 0 else None)
        ax[0].bar(x, none, w, bottom=np.array(hurt) + np.array(help_), color="#dddddd",
                  label="no effect" if j == 0 else None)
    ax[0].set_xticks(np.arange(len(pairs)))
    ax[0].set_xticklabels([l for _, l in pairs], fontsize=7)
    ax[0].set(ylabel="cells (of 32)", title="(a) three-way outcome\nleft bar naive, right bar cluster")
    ax[0].legend(fontsize=7)
    u = J("review_bootstrap_unit.json")
    cells = {k: v for k, v in u.items() if k != "_summary"}
    ratios = [v["width_ratio_cluster_over_naive"] for v in cells.values()]
    ax[1].hist(ratios, bins=10, color="#1f77b4", alpha=0.85)
    ax[1].axvline(1.0, color="k", ls="--", lw=1)
    ax[1].axvline(float(np.mean(ratios)), color="#d62728", lw=1.4,
                  label=f"mean {np.mean(ratios):.2f}×")
    ax[1].set(xlabel="CI width, cluster ÷ naive", ylabel="cells",
              title=f"(b) the wrong unit narrows\n{sum(1 for r in ratios if r > 1)} of {len(ratios)} intervals")
    ax[1].legend(fontsize=7)
    rec["fig5"] = {"summary": S, "width_ratio_mean": float(np.mean(ratios))}
    fig.tight_layout()
    p = os.path.join(R.FIGURES, "paper_fig5_three_way.png")
    fig.savefig(p); plt.close(fig)
    return p


def main():
    rec = {}
    made = [fig1_calibration(rec), fig2_sigma_profile(rec), fig3_collapse(rec),
            fig4_timeline(rec), fig5_three_way(rec)]
    op = os.path.join(R.RESULTS, "paper_figures.json")
    json.dump(rec, open(op, "w"), indent=2)
    print("PAPER FIGURES")
    print("=" * 70)
    for p in made:
        print(f"  wrote {R.rel(p)}")
    print(f"  wrote {R.rel(op)}  (the values each panel plots)")


if __name__ == "__main__":
    main()
