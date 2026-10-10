"""F0 item 3: dry-run both bundle builders' collection and assert nothing under docs/presubmission/round4/
is collected. Round 3's r0_bundle_exclusion.py, adapted. make_anon_bundle.collect() is called as is;
build_supplementary collects inside main(), so its loop is run here on the module's own constants, without
writing a zip, after asserting that the loop below is still the one main() contains (inspect.getsource).
Run from the repository root:  $PY docs/presubmission/round4/f0_bundle_exclusion.py"""
import importlib.util, inspect, os, sys


def load(name):
    spec = importlib.util.spec_from_file_location(name, f"scripts/{name}.py"); m = importlib.util.module_from_spec(spec)
    sys.argv = [name]; spec.loader.exec_module(m); return m


anon, supp = load("make_anon_bundle"), load("build_supplementary")
LOOP = """    files = []
    for d in INCLUDE_DIRS:
        if not os.path.isdir(d):
            continue
        for root, dirs, names in os.walk(d):
            dirs[:] = [x for x in dirs if os.path.join(root, x) not in EXCLUDE_DIRS]
            if "__pycache__" in root:
                continue
            for n in sorted(names):
                if n.endswith(SKIP_SUFFIX):
                    continue
                files.append(os.path.join(root, n))
    files += [f for f in list(INCLUDE_FILES) + list(SHIP_FROM_EXCLUDED) if os.path.exists(f)]
    files = sorted(set(files) - EXCLUDE)
"""
assert LOOP in inspect.getsource(supp.main), "build_supplementary.main()'s collection loop has changed; update this dry run"
a = anon.collect()
files = []
for d in supp.INCLUDE_DIRS:
    if not os.path.isdir(d): continue
    for root, dirs, names in os.walk(d):
        dirs[:] = [x for x in dirs if os.path.join(root, x) not in supp.EXCLUDE_DIRS]
        if "__pycache__" in root: continue
        for n in sorted(names):
            if n.endswith(supp.SKIP_SUFFIX): continue
            files.append(os.path.join(root, n))
files += [f for f in list(supp.INCLUDE_FILES) + list(supp.SHIP_FROM_EXCLUDED) if os.path.exists(f)]
s = sorted(set(files) - supp.EXCLUDE)
r4 = sorted(os.path.join(r, n) for r, _, ns in os.walk("docs/presubmission/round4") for n in ns)
print(f"- files under `docs/presubmission/round4/` on disk: {len(r4)}")
for label, lst, ship in (("`make_anon_bundle.collect()`", a, anon.SHIP_FROM_EXCLUDED),
                         ("`build_supplementary` collection loop", s, supp.SHIP_FROM_EXCLUDED)):
    hits = [f for f in lst if f.startswith("docs/presubmission/round4")]
    pres = [f for f in lst if f.startswith("docs/presubmission/")]
    stray = [p for p in pres if p not in ship]
    print(f"- {label}: {len(lst)} files; under `round4/`: {len(hits)}; under `docs/presubmission/`: "
          f"{', '.join('`'+p+'`' for p in pres)} (all in its SHIP_FROM_EXCLUDED: {'yes' if not stray else 'NO ' + str(stray)})")
    assert not hits, f"{label} collects round4 files: {hits}"
    assert not stray, f"{label} collects docs/presubmission/ files outside SHIP_FROM_EXCLUDED: {stray}"
print("- **PASS**: neither builder collects anything under `docs/presubmission/round4/`.")
