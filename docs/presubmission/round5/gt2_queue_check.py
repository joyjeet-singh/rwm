"""GT2 item 1: the X11 queue finished cleanly and every run record is what the rule queued (reads no evaluation)."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[os.pardir] * 3))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
os.chdir(ROOT)
import x11_common as C  # noqa: E402

q = [l.split() for l in open("runs/queue_round5.txt") if l.strip() and not l.startswith("#")]
ids = [r[0] for r in q]
done = [l.strip() for l in open("runs/queue_round5_done.txt") if l.strip()]
failed = [l.strip() for l in open("runs/queue_round5_failed.txt") if l.strip()] if os.path.exists("runs/queue_round5_failed.txt") else []
log_tail = open("runs/queue_round5.log").read().strip().split("\n")[-1]
rows, bad = [], []
for rid, arch, M, N, seed, iters in q:
    kind, _, fold_s, s = rid.split("_")
    fold = tuple(int(c) for c in fold_s)
    seed = int(seed)
    ens = 5 if kind == "x11" and rid.startswith("x11_e5") else 1
    rec = C.ens5_record(fold, seed) if ens == 5 else C.single_record(fold, seed)
    w = C.ens5_weights(fold, seed) if ens == 5 else C.single_weights(fold, seed)
    probs = []
    if not os.path.exists(rec):
        probs.append("record missing")
    else:
        probs += C.check_record(rec, fold, ens)
        if json.load(open(rec))["seed"] != seed:
            probs.append("seed")
    if not os.path.exists(w) or os.path.getsize(w) == 0:
        probs.append("weights missing or empty")
    if int(iters) != C.ITERS:
        probs.append("queued iterations")
    rows.append({"id": rid, "fold": list(fold), "seed": seed, "ensemble": ens, "record": rec, "weights": w,
                 "weights_bytes": os.path.getsize(w) if os.path.exists(w) else None, "problems": probs})
    bad += [f"{rid}: {p}" for p in probs]
out = {"gate": "GT2 item 1", "log_last_line": log_tail, "queue_ids": len(ids), "done": len(done), "failed": len(failed),
       "all_ids_done": sorted(ids) == sorted(done), "log_ends_empty": log_tail.endswith("queue empty; runner exits"),
       "runs": rows, "problems": bad,
       "pass": not bad and not failed and sorted(ids) == sorted(done) and log_tail.endswith("queue empty; runner exits")}
json.dump(out, open("docs/presubmission/round5/gt2_queue_check.json", "w"), indent=1)
print("GT2 queue check:", "PASS" if out["pass"] else "FAIL", len(ids), "runs;", bad[:5])
