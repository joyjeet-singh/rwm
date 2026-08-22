"""Clean-clone check: diff every regenerated number against the committed values.

IMPORTANT -- what "regenerated" means here. A clean clone already contains every
committed artifact, so a file the pipeline never rewrites still compares identical.
Counting those as "regenerated bitwise" overstates the test by an order of magnitude:
the figure once published (258,700) was in fact every numeric value in the committed
results/ directory, of which --quick rewrites well under a tenth.

reproduce.sh now records each output it actually regenerates in results/_regenerated.txt.
If that file is present, the counts below are partitioned: REGENERATED files are the
real test, COPIED files are reported separately and never folded into the headline.
"""
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
# Whole artifacts that measure the machine rather than the model. step4_5_timing.json
# is the CPU budget: every number in it -- projected runtimes, peak RSS, the standard
# deviation across repeats -- is host-dependent. The key-level TIMING filter above did
# not catch proj_500_s, proj_2500_s, peak_rss_mb or std, so this file alone produced
# every difference in the first honest clean-clone comparison.
MACHINE_FILES = ("step4_5_timing.json",)


def time_bounded(d):
    """True if this artifact's run stopped on a WALL-CLOCK budget rather than its
    iteration cap, which makes its iteration count and terminal losses a property
    of the host, not the model.

    Derived from the artifact instead of hardcoded by filename, because it is not a
    property of the file -- it is a property of the run. step4_4_overfit_b32lr1e3
    and step4_4_overfit_ens1 come from the same script: the first was given a
    100,000 s budget and stopped at its 2,000-iteration cap, so it reproduces
    bitwise and IS checked; the second was given 2,700 s and stopped at 451
    iterations on one machine and 514 on another, so it is not comparable and is
    excluded. Excluding by filename would have dropped the reproducible one too.
    """
    try:
        c = d.get("config") or {}
        cap, budget, ran = c.get("iters"), c.get("max_seconds"), d.get("iterations_run")
        return (cap is not None and budget is not None and ran is not None
                and ran < cap)
    except Exception:
        return False
regen=set()
_rl=os.path.join(A,"_regenerated.txt")
if os.path.exists(_rl):
    regen={l.strip() for l in open(_rl) if l.strip()}
tot=exact=close=diff=timing=nans=0; report=[]; dropped=[]; machine=0
time_bounded_files=[]      # excluded because the RUN was wall-clock bounded
c_tot=c_exact=c_diff=0     # files present in the clone but never rewritten
for fn in sorted(os.listdir(B)):
    if not fn.endswith(".json"): continue
    pa, pb = os.path.join(A, fn), os.path.join(B, fn)
    if not os.path.exists(pa): continue
    try: da, db = json.load(open(pa)), json.load(open(pb))
    except Exception: continue
    ma, mb = dict(flat(da)), dict(flat(db))
    if fn in MACHINE_FILES or time_bounded(db) or time_bounded(da):
        machine += sum(1 for k in mb if k in ma)
        if fn not in MACHINE_FILES:
            time_bounded_files.append(fn)
        continue
    is_regen = (not regen) or (fn in regen)
    # A key in the committed file with no counterpart in the regenerated one is a
    # DELETION, not a match. Silently skipping these once hid three hand-added
    # convention blocks in manifest.json that the pipeline destroys on regeneration.
    if is_regen:
        gone = [k for k in mb if k not in ma]
        if gone: dropped.append((fn, len(gone), gone[:6]))
    for k in mb:
        if k not in ma: continue
        if any(t in k for t in TIMING): timing += 1; continue
        x, y = ma[k], mb[k]
        if not is_regen:
            c_tot += 1
            if x == y or (math.isnan(x) and math.isnan(y)): c_exact += 1
            else: c_diff += 1
            continue
        tot += 1
        if math.isnan(x) and math.isnan(y): nans += 1; exact += 1
        elif x == y: exact += 1
        elif math.isclose(x, y, rel_tol=1e-9, abs_tol=1e-12): close += 1
        else:
            diff += 1
            if len(report) < 15:
                r = abs(x-y)/max(abs(x), abs(y), 1e-30)
                report.append((fn, k, y, x, r))
print("="*90); print("CLEAN-CLONE NUMERIC VERIFICATION"); print("="*90)
print(f"  regenerated-file values compared : {tot}"
      + ("" if regen else "   (no results/_regenerated.txt -- ALL files treated as regenerated)"))
print(f"    of which NaN in both  : {nans}  (counted identical: NaN != NaN in IEEE 754)")
print(f"  machine-measurement files excluded : {machine} values in {', '.join(MACHINE_FILES)}")
if time_bounded_files:
    print(f"  wall-clock-bounded runs excluded   : {len(time_bounded_files)} file(s) -- "
          f"{', '.join(time_bounded_files)}")
    print("      (stopped on --max-seconds, not the iteration cap, so the iteration count and")
    print("       terminal losses measure the host; sibling runs from the same script that")
    print("       reached their cap ARE checked, and reproduce bitwise)")
print(f"  timing fields excluded  : {timing}  (machine-dependent by design, see README)")
print(f"  bitwise identical       : {exact} ({100*exact/max(tot,1):.2f}%)")
print(f"  identical to 1e-9       : {close}")
print(f"  DIFFERING               : {diff}")
for fn,k,c,r_,rel in report:
    print(f"    {fn}{k}\n      committed {c!r}  regenerated {r_!r}  rel {rel:.2e}")
print(f"\n  keys present in the committed file but MISSING after regeneration: "
      f"{sum(n for _,n,_ in dropped)} in {len(dropped)} file(s)")
for fn,n,ex in dropped:
    print(f"    !! {fn}: {n} values lost, e.g. {', '.join(ex[:3])}")
if regen:
    print(f"\n  files actually regenerated by this run : {len(regen)}")
    print(f"  values in copied (not regenerated) files: {c_tot}  "
          f"[identical {c_exact}, differing {c_diff}]")
    print("    Copied files are NOT part of the reproducibility claim -- a clean clone")
    print("    contains them already. They are reported for completeness only.")
json.dump({"regenerated_files": sorted(regen), "values_compared": tot,
           "bitwise_identical": exact, "identical_to_1e-9": close, "differing": diff,
           "timing_excluded": timing, "nan_in_both": nans,
           "copied_file_values": c_tot, "copied_identical": c_exact,
           "copied_differing": c_diff,
           "machine_file_values_excluded": machine,
           "machine_files": list(MACHINE_FILES),
           "time_bounded_files_excluded": time_bounded_files},
          open(os.path.join(B, "verify_reproduction.json"), "w"), indent=2)
print(f"\n  wrote {os.path.join(B, 'verify_reproduction.json')}")
ok = (diff == 0) and not dropped
print(f"\n  RESULT: {'PASS — every regenerated number matches' if ok else 'DIFFERENCES OR DELETIONS FOUND'}")
sys.exit(0 if ok else 1)
