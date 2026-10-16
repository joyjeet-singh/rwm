"""F10: a correction to M-65's discharge record (the ledger is append-only; M-65 is not edited). Its paragraph says the
oracle-rescaled coverage lands "at or above 68.27% everywhere"; two cells fall below 68.27%, inside the band. Every figure
is read from results/m65_gaussian_nominal.json. Writes .bak copies outside the repository and refuses to run twice.
  $PY docs/presubmission/round4/f10_write_m65_correction.py
"""
import json, os, re, shutil
L, RES, BAK = "FINDINGS_LEDGER.md", "RESULTS.md", "/Users/Shared/rwm_verify/evidence/R4F10/fix"
led = open(L, encoding="utf-8").read()
m65 = re.search(r"^### M-65 — .*?(?=^### |\Z)", led, re.M | re.S).group(0)
assert "coverage lands at or above 68.27% everywhere" in " ".join(m65.split()), "M-65 does not carry the quoted wording"
assert "Corrects** M-65" not in led, "already written"
d = json.load(open("results/m65_gaussian_nominal.json"))
nom = d["targets"]["pm1_pct"] if isinstance(d.get("targets"), dict) and "pm1_pct" in d["targets"] else 68.27
lo = re.fullmatch(r"below (\d+\.\d+)", d["thresholds_committed_in_advance"]["HEAVY-TAILED"]).group(1)
hi = re.fullmatch(r"above (\d+\.\d+)", d["thresholds_committed_in_advance"]["OVER-DISPERSED"]).group(1)
below = [(c, h, cell["coverage_pm1_oracle_pct"], cell["verdict"]) for c, v in d["cases"].items()
         for h, cell in v["by_horizon"].items() if cell["coverage_pm1_oracle_pct"] < nom]
assert len(below) == 2 and all(float(lo) < x[2] and x[3] == "GAUSSIAN NOMINAL ADEQUATE" for x in below), below
n = sum(len(v["by_horizon"]) for v in d["cases"].values()); cnt = d["verdict"]["counts"]
nm = max(int(x) for x in re.findall(r"^### M-(\d+) ", led, re.M)) + 1
cells = "; ".join(f"{c}, h = {h}, {x:.2f}%" for c, h, x, _ in below)
entry = f"""
### M-{nm} — Correction to M-65's discharge record: two of its in-band cells fall below the nominal · **NEW**
**Corrects** M-65, whose discharge paragraph says that under an oracle rescale "coverage lands at or above 68.27%
everywhere". In `results/m65_gaussian_nominal.json` {len(below)} of the {n} cells fall below {nom}%: {cells}. Both lie inside
the band the rule committed in advance, [{lo}%, {hi}%], so M-65's returned reading stands as it was: NOT HEAVY-TAILED in
every one of {n} cells, {cnt.get("GAUSSIAN NOMINAL ADEQUATE", 0)} GAUSSIAN NOMINAL ADEQUATE and {cnt.get("OVER-DISPERSED", 0)} OVER-DISPERSED. No verdict moves, and M-65 is not
edited. The paper carried the same wording in the sentence round 4 moved from §3.1 to Appendix G; it now states the
rule's heavy-tail bound and its two counts. Appendix E had printed M-65's first defined branch, GAUSSIAN NOMINAL ADEQUATE,
because the returned phrase wraps a line and `scripts/appendix_g_rules.py` did not read past it; it now prints the
returned reading. Found by F10's read-only review of Appendices A–M and checked against the artifact.
**Evidence** `RUN` `results/m65_gaussian_nominal.json`; `SRC` `scripts/appendix_g_rules.py`
**Status** CONFIRMED · **Relevance** METHOD
"""
R_ = open(RES, encoding="utf-8").read()
row = re.search(r"^(\| `M-` methodological findings \| )(\d+)( \|)", R_, re.M)
assert row and int(row.group(2)) == nm - 1, row
os.makedirs(BAK, exist_ok=True)
shutil.copy(L, f"{BAK}/FINDINGS_LEDGER.md.m65.bak"); shutil.copy(RES, f"{BAK}/RESULTS.md.m65.bak")
open(L, "w", encoding="utf-8").write(led.rstrip("\n") + "\n" + entry)
open(RES, "w", encoding="utf-8").write(R_.replace(row.group(0), f"{row.group(1)}{nm}{row.group(3)}", 1))
print(f"appended M-{nm}; RESULTS.md M- {nm - 1} -> {nm}")
