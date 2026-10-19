"""
Round 5, G6 item 1: each check that reads docs/SUPPLEMENT must still fail when a violation sits in the supplement.

A passage moved out of the PDF must stay checked. For each tool this plants one violation into the supplement (template
or built, whichever that tool reads), runs the tool, requires it to catch the plant, and restores every file it touched,
verified by SHA-256. Tools that write an artifact have it restored too, so a self-test never changes a committed result.

  comparative claims   a retracted assertion (C10.1's) planted in docs/SUPPLEMENT.template.md
  typed numeral audit  a typed measurement (its own --plant-supplement mode)
  restatement index    a typed copy of a placeholder's value in that placeholder's own sentence
  horizon sweep        a calibration figure with no horizon
  xref sweep           a pointer to an artifact that does not exist, planted in docs/SUPPLEMENT.md
  scope audit          its own corrupt-and-catch self-test

    python scripts/supplement_selftest.py
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import placeholders as PH  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
PY = sys.executable
GUARD = [PH.SUPPLEMENT_TEMPLATE, PH.SUPPLEMENT, "results/comparative_claims.json", "results/typed_numerals.json",
         "results/restatement_index.json", "results/horizon_sweep.json", "results/xref_sweep.json",
         "results/check_scope_audit.json"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None


def run(args):
    r = subprocess.run([PY] + args, cwd=ROOT, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def plant(path, text):
    with open(path, "a") as f:
        f.write("\n\n" + text + "\n")


def main():
    os.chdir(ROOT)
    before = {p: sha(p) for p in GUARD}
    bak = tempfile.mkdtemp()
    for p in GUARD:
        if os.path.exists(p):
            shutil.copy(p, os.path.join(bak, p.replace("/", "__")))
    res = {}
    try:
        def restore():
            for p in GUARD:
                b = os.path.join(bak, p.replace("/", "__"))
                if os.path.exists(b):
                    shutil.copy(b, p)

        # comparative claims: C10.1's retracted assertion, in the supplement template
        plant(PH.SUPPLEMENT_TEMPLATE, "The checkpoint cannot have come from the released recipe.")
        rc, out = run(["scripts/check_comparative_claims.py"])
        res["comparative_claims"] = bool(rc != 0 and re.search(r"FAIL\s+C10\.1", out))
        restore()

        # typed numeral audit: its own plant mode
        rc, out = run(["scripts/typed_numeral_audit.py", "--plant-supplement"])
        res["typed_numeral_audit"] = bool(rc == 0 and "caught the planted measurement" in out)
        restore()

        # restatement index: a template sentence binding a placeholder with "=", retyped with its value, appended to the
        # supplement. The first candidate (in template order) whose retyped copy the index flags is the plant; the
        # self-test passes only if one is found and it is flagged from inside the supplement.
        import restatement_index as RI
        tpl = open("PAPER.template.md").read()
        N = json.load(open("results/paper_numbers.json"))
        base = PH.with_supplement(tpl)
        n0 = len(RI.typed_restatements(base, N))
        found = None
        for m in re.finditer(r"[^.\n]*=\s*\{\{([A-Za-z0-9_]+)\}\}[^.\n]*\.", tpl):
            k = m.group(1)
            v = str(N.get(k, {}).get("value", ""))
            if not re.fullmatch(r"[-+]?\d[\d,]*\.\d+", v) or k in RI.GRID_KEYS:
                continue
            typed = PH.PH.sub(lambda x: str(N[x.group(1)]["value"]) if x.group(1) in N else "", m.group(0))
            hits = [x for x in RI.typed_restatements(base + "\n\n" + typed + "\n", N) if x["key"] == k]
            if len(RI.typed_restatements(base + "\n\n" + typed + "\n", N)) > n0 and hits:
                found = {"key": k, "value": v}
                break
        res["restatement_index"] = found is not None
        restore()

        # horizon sweep: a calibration figure with no horizon named
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as t:
            t.write(PH.with_supplement(tpl) + "\n\nThe epistemic term is {{d1n_epi_ratio_h100}}× overconfident.\n")
        rc, out = run(["scripts/horizon_sweep.py", "--file", t.name])
        res["horizon_sweep"] = bool(rc != 0 and "d1n_epi_ratio_h100" in out)
        os.unlink(t.name)
        restore()

        # xref sweep: a missing artifact, in the built supplement
        plant(PH.SUPPLEMENT, "The table is in `results/does_not_exist_g6_probe.json`.")
        rc, out = run(["scripts/xref_sweep.py"])
        res["xref_sweep"] = bool("does_not_exist_g6_probe" in out and "MISSING" in out)
        restore()

        rc, out = run(["scripts/check_scope_audit.py", "--self-test"])
        res["check_scope_audit"] = bool(rc == 0 and "PASS" in out)
        restore()
    finally:
        for p in GUARD:
            b = os.path.join(bak, p.replace("/", "__"))
            if os.path.exists(b):
                shutil.copy(b, p)
        shutil.rmtree(bak)
    after = {p: sha(p) for p in GUARD}
    restored = before == after
    for k, v in res.items():
        print(f"  {k:<22} {'caught' if v else 'NOT CAUGHT'}")
    print(f"  every touched file restored byte-identically: {restored}")
    ok = restored and all(res.values()) and len(res) == 6
    print(f"  SUPPLEMENT SELF-TEST: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
