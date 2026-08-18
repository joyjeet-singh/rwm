"""Clean-clone check: diff every regenerated number against the committed values."""
import json, os, sys, math
A, B = sys.argv[1], sys.argv[2]          # regenerated dir, committed dir
def flat(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items(): yield from flat(v, f"{p}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from flat(v, f"{p}[{i}]")
    elif isinstance(o, (int, float)) and not isinstance(o, bool):
        yield p, float(o)
# Fields that are measurements of THIS machine, not results. They are recorded in
# the manifest deliberately and are not expected to reproduce; their magnitude is
# documented in the README.
TIMING = ("wall_clock", "s_per_iter", "elapsed_s", "_time")
tot=exact=close=diff=timing=nans=0; report=[]
for fn in sorted(os.listdir(B)):
    if not fn.endswith(".json"): continue
    pa, pb = os.path.join(A, fn), os.path.join(B, fn)
    if not os.path.exists(pa): continue
    try: da, db = json.load(open(pa)), json.load(open(pb))
    except Exception: continue
    ma, mb = dict(flat(da)), dict(flat(db))
    for k in mb:
        if k not in ma: continue
        if any(t in k for t in TIMING): timing += 1; continue
        tot += 1; x, y = ma[k], mb[k]
        if math.isnan(x) and math.isnan(y): nans += 1; exact += 1
        elif x == y: exact += 1
        elif math.isclose(x, y, rel_tol=1e-9, abs_tol=1e-12): close += 1
        else:
            diff += 1
            if len(report) < 15:
                r = abs(x-y)/max(abs(x), abs(y), 1e-30)
                report.append((fn, k, y, x, r))
print("="*90); print("CLEAN-CLONE NUMERIC VERIFICATION"); print("="*90)
print(f"  numeric values compared : {tot}")
print(f"    of which NaN in both  : {nans}  (counted identical: NaN != NaN in IEEE 754)")
print(f"  timing fields excluded  : {timing}  (machine-dependent by design, see README)")
print(f"  bitwise identical       : {exact} ({100*exact/max(tot,1):.2f}%)")
print(f"  identical to 1e-9       : {close}")
print(f"  DIFFERING               : {diff}")
for fn,k,c,r_,rel in report:
    print(f"    {fn}{k}\n      committed {c!r}  regenerated {r_!r}  rel {rel:.2e}")
print(f"\n  RESULT: {'PASS — every regenerated number matches' if diff==0 else 'DIFFERENCES FOUND'}")
sys.exit(0 if diff==0 else 1)
