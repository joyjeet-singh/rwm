"""R5 item H4: the CPU jobs round 2's sessions logged while rule X1's Part C queue ran, for the overlap column of
Appendix B's runtime table. The counterpart of docs/presubmission/s8_cpu_jobs.json, for the second queue.

Round 2's session log lists those jobs without times (T2 and T3, docs/presubmission/round2/SESSION_LOG.md). Each
build-and-check pass left its step logs in the session's evidence directory, so their modification times date it: a
pass runs from its first log's modification time to its last. That misses the first step's own duration, so every
start is late by that much; the basis says so. A pass that stopped at its first step (one log file) is not a CPU job
over a minute and is left out, as S8's list leaves out jobs under a minute.

Reads runs/queue_round2.log (gitignored) for the queue's window and the evidence directory outside the repository, so
it runs only on the machine that ran the queue. Writes docs/presubmission/x1_partc_cpu_jobs.json. Run from the
repository root.
"""
import collections
import datetime as D
import json
import os
import re

EV = "/Users/Shared/rwm_verify/evidence/R2T2"
TZ = D.timezone(D.timedelta(hours=5, minutes=30))
OUT = "docs/presubmission/x1_partc_cpu_jobs.json"

t = {}
for l in open("runs/queue_round2.log"):
    m = re.match(r"(\S+ \S+) queue (?:runner start|empty)", l)
    if m:
        t.setdefault("start" if "start" in l else "end", D.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S")
                     .replace(tzinfo=TZ))
assert set(t) == {"start", "end"}, t

passes = collections.defaultdict(list)
for f in os.listdir(EV):
    m = re.match(r"(t\d\w*?)_(b1|b2|g|sha)_", f)
    if m:
        passes[m.group(1)].append(D.datetime.fromtimestamp(os.path.getmtime(os.path.join(EV, f)), TZ))
jobs, short = [], []
for k, ts in sorted(passes.items(), key=lambda kv: min(kv[1])):
    s, e = min(ts), max(ts)
    if e < t["start"] or s > t["end"]:
        continue                                   # outside the queue's window
    if len(ts) == 1:
        short.append(k)
        continue
    jobs.append({"job": f"build-and-check pass ({k})", "start": s.isoformat(timespec="seconds"),
                 "end": e.isoformat(timespec="seconds"), "seconds": round((e - s).total_seconds()),
                 "basis": "exact end, late start: the pass's step logs' modification times, first to last "
                          "(the first step's own duration is not included)"})
assert jobs and all(len(passes[k]) == 1 for k in short)
out = {"what": "every CPU job over one minute logged by round 2's sessions while rule X1's Part C queue ran "
               "(runs/queue_round2.txt), for Appendix B's overlap column",
       "timezone": "+05:30",
       "queue_window": {k: v.isoformat(timespec="seconds") for k, v in t.items()},
       "source": "the step logs each build-and-check pass left in round 2's T2/T3 evidence directory "
                 "(outside the repository); their modification times are copied here",
       "left_out": {"passes that stopped at their first step (one log file)": short},
       "n_jobs": len(jobs), "jobs": jobs}
json.dump(out, open(OUT, "w"), indent=1)
open(OUT, "a").write("\n")
print(f"{len(jobs)} passes in {t['start']:%H:%M:%S}-{t['end']:%H:%M:%S}; left out {short}")
for j in jobs:
    print(f"  {j['job']:34} {j['start'][11:19]}-{j['end'][11:19]}")
