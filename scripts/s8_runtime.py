"""S8 step 4 -- the pre-submission runs' runtime inputs, for Appendix B.

Appendix B's runtime figures (`rt_*` in scripts/paper_numbers.py) are computed from
results/step5_*.json only, and its prose describes those runs: "the other N hours" are the
released-width runs, which the architecture baselines are not. So this does not fold the 42
pre-submission runs into those keys. It records their per-run `wall_clock_s` beside them, for
S9 to write in, and flags every run that overlapped a CPU job a session logged: each such job
inflates the `wall_clock_s` of the run it overlaps, which is the training-time half M-74
reports.

Inputs: runs/queue.txt and runs/queue.log (gitignored, so their start and end times are
copied into the output), each run's own artifact, and docs/presubmission/s8_cpu_jobs.json.

Round 3, R5 (H4): rule X1's Part C ran from a second queue (runs/queue_round2.txt and .log), which
this script did not read, so Appendix B's table left its two runs out. They are recorded under
`x1_part_c`, beside the queue above rather than in its totals: those are the sweep's and the
baselines' runs, which Appendix B's prose counts. Their overlaps are against the CPU jobs round 2's
sessions logged while that queue ran (docs/presubmission/x1_partc_cpu_jobs.json).

    python scripts/s8_runtime.py      -> results/presubmission_runtime.json
(moved from docs/presubmission/ in round 2, T8; reproduce.sh stage 20t7 runs it)
"""
import datetime as D
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))   # scripts/ -> repo (moved in round 2, T8)
TZ = D.timezone(D.timedelta(hours=5, minutes=30))


def queue_times(log):
    start, end = {}, {}
    for l in open(os.path.join(ROOT, "runs", log)):
        m = re.match(r"(\S+ \S+) (start|done)\s+(\S+)", l)
        if m:
            t = D.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ)
            (start if m.group(2) == "start" else end)[m.group(3)] = t
    return start, end


def logged_jobs(path):
    jobs = json.load(open(os.path.join(ROOT, path)))["jobs"]
    return jobs, [(j, D.datetime.fromisoformat(j["start"]), D.datetime.fromisoformat(j["end"]))
                  for j in jobs if j["start"]]


def x1_part_c():
    """Rule X1's Part C: the second queue's runs, each with its overlaps against round 2's logged jobs."""
    queue = [l.split() for l in open(os.path.join(ROOT, "runs", "queue_round2.txt"))
             if l.strip() and not l.startswith("#")]
    start, end = queue_times("queue_round2.log")
    jobs_path = "docs/presubmission/x1_partc_cpu_jobs.json"
    _, timed = logged_jobs(jobs_path)
    runs, fams = [], {}
    for rid, arch, m, n, seed, iters in queue:
        a, regime, spec = arch.split("-")
        assert (a, regime) == ("rssm", "tf") and spec.startswith("x1v"), arch
        art = f"results/baseline_run_{a}_{regime}_{spec}_seed{seed}.json"
        A = json.load(open(os.path.join(ROOT, art)))
        assert A["hyperparameters"]["iterations"] == int(iters), (art, iters)
        s, e = start[rid], end[rid]
        over = []
        for j, js, je in timed:
            ov = (min(e, je) - max(s, js)).total_seconds()
            if ov > 0:
                over.append({"job": j["job"], "overlap_s": round(ov), "basis": j["basis"].split(":")[0]})
        fam = f"{a}_{regime}_{spec}"
        runs.append({"run": rid, "rule": "X1", "family": fam, "seed": int(seed),
                     "start": s.isoformat(timespec="seconds"), "end": e.isoformat(timespec="seconds"),
                     "wall_clock_s": A["wall_clock_s"], "artifact": art,
                     "overlapping_logged_jobs": over,
                     "overlap_s": sum(o["overlap_s"] for o in over)})
        fams.setdefault(fam, []).append(A["wall_clock_s"])
    return {"what": "rule X1's Part C runs (runs/queue_round2.txt), outside n_runs and wall_clock_s above",
            "sources": ["runs/queue_round2.txt", "runs/queue_round2.log (gitignored; times copied here)",
                        "results/baseline_run_rssm_tf_x1v*_seed0.json", jobs_path],
            "n_runs": len(runs), "wall_clock_s": sum(r["wall_clock_s"] for r in runs),
            "by_family": {k: {"n_runs": len(v), "wall_clock_s": sum(v), "mean_s": sum(v) / len(v)}
                          for k, v in fams.items()},
            "n_runs_overlapped": sum(1 for r in runs if r["overlap_s"] > 0),
            "runs": runs}


def main():
    queue = [l.split() for l in open(os.path.join(ROOT, "runs", "queue.txt"))
             if l.strip() and not l.startswith("#")]
    start, end = {}, {}
    for l in open(os.path.join(ROOT, "runs", "queue.log")):
        m = re.match(r"(\S+ \S+) (start|done)\s+(\S+)", l)
        if m:
            t = D.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ)
            (start if m.group(2) == "start" else end)[m.group(3)] = t
    jobs = json.load(open(os.path.join(ROOT, "docs", "presubmission", "s8_cpu_jobs.json")))["jobs"]
    timed = [(j, D.datetime.fromisoformat(j["start"]), D.datetime.fromisoformat(j["end"]))
             for j in jobs if j["start"]]

    runs, fams = [], {}
    for rid, arch, m, n, seed, iters in queue:
        if arch == "rwm":
            art = f"results/mn_sweep_run_M{m}_N{n}_seed{seed}.json"
            rule, fam = "M-74", f"M{m}_N{n}"
        else:
            a, regime, spec = arch.split("-")
            art = f"results/baseline_run_{a}_{regime}_{spec}_seed{seed}.json"
            rule, fam = ("M-75" if regime == "tf" else "M-76"), f"{a}_{regime}_{spec}"
        A = json.load(open(os.path.join(ROOT, art)))
        s, e = start[rid], end[rid]
        over = []
        for j, js, je in timed:
            ov = (min(e, je) - max(s, js)).total_seconds()
            if ov > 0:
                over.append({"job": j["job"], "overlap_s": round(ov), "basis": j["basis"].split(":")[0]})
        runs.append({"run": rid, "rule": rule, "family": fam, "seed": int(seed),
                     "start": s.isoformat(timespec="seconds"), "end": e.isoformat(timespec="seconds"),
                     "wall_clock_s": A["wall_clock_s"], "artifact": art,
                     "overlapping_logged_jobs": over,
                     "overlap_s": sum(o["overlap_s"] for o in over)})
        fams.setdefault((rule, fam), []).append(A["wall_clock_s"])

    by_rule = {}
    for r in runs:
        b = by_rule.setdefault(r["rule"], {"n_runs": 0, "wall_clock_s": 0.0})
        b["n_runs"] += 1
        b["wall_clock_s"] += r["wall_clock_s"]
    out = {"what": "per-run wall-clock of the pre-submission queue (M-74 sweep, M-75 and M-76 baselines), "
                   "with every overlap against a logged CPU job",
           "sources": ["runs/queue.txt", "runs/queue.log (gitignored; times copied here)",
                       "results/mn_sweep_run_*.json", "results/baseline_run_*.json",
                       "docs/presubmission/s8_cpu_jobs.json"],
           "note": "a job logged only as a window, or with no times, is matched against that window or "
                   "not at all; its 'basis' says which. Overlap inflates wall_clock_s; it does not change "
                   "any trained weight or any verdict.",
           "n_runs": len(runs), "wall_clock_s": sum(r["wall_clock_s"] for r in runs),
           "by_rule": by_rule,
           "by_family": {f"{k[0]} {k[1]}": {"n_runs": len(v), "wall_clock_s": sum(v),
                                            "mean_s": sum(v) / len(v)} for k, v in fams.items()},
           "n_runs_overlapped": sum(1 for r in runs if r["overlap_s"] > 0),
           "unassignable_jobs": [j["job"] for j in jobs if not j["start"]],
           "runs": runs,
           "x1_part_c": x1_part_c()}
    json.dump(out, open(os.path.join(ROOT, "results", "presubmission_runtime.json"), "w"), indent=1)
    print(f"{len(runs)} runs, {out['wall_clock_s']/3600:.2f} h in all; "
          + ", ".join(f"{k} {v['n_runs']} runs {v['wall_clock_s']/3600:.2f} h" for k, v in by_rule.items()))
    print(f"{out['n_runs_overlapped']} runs overlapped a logged CPU job:")
    for r in runs:
        if r["overlap_s"]:
            print(f"  {r['run']:26} {r['overlap_s']:5d} s over {len(r['overlapping_logged_jobs'])} job(s)"
                  f" ({', '.join(sorted({o['basis'] for o in r['overlapping_logged_jobs']}))})")
    xc = out["x1_part_c"]
    print(f"rule X1 Part C, outside those: {xc['n_runs']} runs, {xc['wall_clock_s']/3600:.2f} h; "
          f"{xc['n_runs_overlapped']} overlapped a logged CPU job")
    for r in xc["runs"]:
        print(f"  {r['run']:26} {r['overlap_s']:5d} s over {len(r['overlapping_logged_jobs'])} job(s)")


if __name__ == "__main__":
    main()
