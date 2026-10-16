"""F9 H2: the CPU jobs round 4's sessions ran while the round-4 queue trained, for Appendix B's overlap column.

The precedent is docs/presubmission/x1_partc_cpu_jobs.json: the evidence files each session's jobs wrote, outside the
repository, give their times. Here every file under /Users/Shared/rwm_verify/evidence/R4F1 to R4F4 modified inside one
of the queue's two windows is read. Grouping those times into separate jobs fails on a job that writes one file, at its
end (X8's dry runs, about 9 min each, wrote one log apiece), so each session is one job: its window runs from its first
such file to its last, the basis is "session window", and the job is the session's logged CPU work, which its
SESSION_LOG entry records as contended with the queue (F2-F4) or as the build after launch (F1). Work before a session's
first file is not covered ("late start"). The queue's windows come from runs/queue_round4.log and the run records.

Writes docs/presubmission/round4/f9_cpu_jobs.json.
  $PY docs/presubmission/round4/f9_cpu_jobs.py
"""
import datetime as D
import json
import os

EV = "/Users/Shared/rwm_verify/evidence"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "f9_cpu_jobs.json")
TZ = D.timezone(D.timedelta(hours=5, minutes=30))
# The queue's two runners: the first from its launch (F1) to the last run it finished, the second as its log states.
WINDOWS = [(D.datetime(2026, 10, 11, 10, 36, 0, tzinfo=TZ), D.datetime(2026, 10, 12, 6, 31, 0, tzinfo=TZ)),
           (D.datetime(2026, 10, 14, 22, 26, 14, tzinfo=TZ), D.datetime(2026, 10, 15, 5, 4, 17, tzinfo=TZ))]
by_sess = {}
for sess in ("R4F1", "R4F2", "R4F3", "R4F4"):
    for root, _, names in os.walk(os.path.join(EV, sess)):
        for nm in names:
            p = os.path.join(root, nm)
            t = D.datetime.fromtimestamp(os.path.getmtime(p), TZ)
            if any(a <= t <= b for a, b in WINDOWS):
                by_sess.setdefault(sess, []).append(t)
files = [t for v in by_sess.values() for t in v]
LOGGED = {"R4F1": "the build and gates after the queue's launch (SESSION_LOG F1)",
          "R4F2": "X6-X8's producers' re-runs, assertions, dry runs and readings, and the build (SESSION_LOG F2)",
          "R4F3": "N5, N6's stage 20o regeneration and three builds (SESSION_LOG F3)",
          "R4F4": "about eight builds with gates and the figures (SESSION_LOG F4)"}
jobs = []
for sess, ts in sorted(by_sess.items()):
    s, e = min(ts), max(ts)
    jobs.append({"job": f"{sess[2:]}: {LOGGED[sess]}", "session": sess, "start": s.isoformat(timespec="seconds"),
                 "end": e.isoformat(timespec="seconds"), "seconds": round((e - s).total_seconds()), "n_files": len(ts),
                 "basis": "session window: the session's evidence files' modification times, first to last (late start)"})
unassignable = [
    {"job": "F1's review agent (about 16 min)", "session": "R4F1", "start": None, "end": None, "basis": "logged without times: SESSION_LOG F1"},
    {"job": "F2's review agent (about 14 min)", "session": "R4F2", "start": None, "end": None, "basis": "logged without times: SESSION_LOG F2"},
    {"job": "F4's review workflow, 2 agents (12.4 min wall)", "session": "R4F4", "start": None, "end": None, "basis": "logged without times: SESSION_LOG F4"},
    {"job": "the session that resumed the queue on 2026-10-14 logged no CPU jobs", "session": None, "start": None, "end": None,
     "basis": "round4/OUT_OF_SCOPE.md: its work, if any, is unrecorded"}]
out = {"what": "every CPU job over one minute that round 4's sessions F1-F4 ran while the round-4 queue trained "
               "(runs/queue_round4.txt), for Appendix B's overlap column",
       "timezone": "+05:30",
       "queue_windows": [{"start": a.isoformat(timespec="seconds"), "end": b.isoformat(timespec="seconds")} for a, b in WINDOWS],
       "source": "the files round 4's sessions F1-F4 wrote to their evidence directories (outside the repository); "
                 "their modification times are copied here",
       "grouping": "one job per session, its window from its first evidence file to its last inside the queue's windows",
       "n_files": len(files), "n_jobs": len(jobs), "jobs": jobs + unassignable}
json.dump(out, open(OUT, "w"), indent=1)
print(f"{len(files)} files in the queue's windows -> {len(jobs)} timed jobs, {len(unassignable)} logged without times")
for j in jobs:
    print(f"  {j['start'][5:16]} -> {j['end'][11:16]} {j['seconds']:5d} s  {j['session']}")
