"""R0 item 3: dry-run both bundle builders' collection and assert nothing under docs/presubmission/round3/
is collected. make_anon_bundle.collect() is called as is; build_supplementary collects inside main(), so its
loop is run verbatim on the module's own constants, without writing a zip. Run from the repository root."""
import importlib.util, os, sys
def load(name):
    spec = importlib.util.spec_from_file_location(name, f"scripts/{name}.py"); m = importlib.util.module_from_spec(spec)
    sys.argv = [name]; spec.loader.exec_module(m); return m
anon, supp = load("make_anon_bundle"), load("build_supplementary")
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
r3 = sorted(os.path.join(r, n) for r, _, ns in os.walk("docs/presubmission/round3") for n in ns)
print(f"- files under `docs/presubmission/round3/` on disk: {len(r3)}")
for label, lst in (("`make_anon_bundle.collect()`", a), ("`build_supplementary` collection loop", s)):
    hits = [f for f in lst if f.startswith("docs/presubmission/round3")]
    pres = [f for f in lst if f.startswith("docs/presubmission/")]
    print(f"- {label}: {len(lst)} files; under `round3/`: {len(hits)}; under `docs/presubmission/`: {', '.join('`'+p+'`' for p in pres)} (SHIP_FROM_EXCLUDED)")
    assert not hits, f"{label} collects round3 files: {hits}"
print("- **PASS**: neither builder collects anything under `docs/presubmission/round3/`.")
