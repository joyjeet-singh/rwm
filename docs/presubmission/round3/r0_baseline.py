"""R0 item 4: the round-3 baselines, written to docs/presubmission/round3/BASELINE_R0.md.

Round 2's t0_baseline.py, adapted. One fast build (FILE_MAP §3), then every gate, then the two gates
outside the fast build (part_f_gate with the identity configured and no clone, and submission_check),
each recorded as exit code plus its summary line. Then:
  - main-text words by docs/presubmission/round2/t6_words.py's rule (FILE_MAP §13: whitespace tokens,
    str.split(), from `## 1. Introduction`), to "Data and code" and to "References", in total and per
    `##`/`###` section;
  - the page count, from compile_paper.py's own output;
  - the abstract's word and numeral counts and caps exactly as submission gate C12.1 computes them
    (read from results/comparative_claims.json, which check_comparative_claims.py writes);
  - the set of {{keys}} PAPER.template.md uses, written to round3/r0_template_keys.txt, so R6 and R7 can
    diff it (PLAN Annex 4 item 7).
Every figure is read from what the scripts print or from PAPER.md; none is typed. Tracked files that a
gate rewrites as a side effect (PAPER.pdf's timestamps, results/part_f_gate.json) are restored
afterwards, as S0 and T0 did, and the tree is asserted unchanged. Logs go to $R0_LOGS (outside the
repository). Run from the repository root:  $PY docs/presubmission/round3/r0_baseline.py
"""
import os, re, subprocess, sys, json, datetime

PY = sys.executable
LOGS = os.environ.get("R0_LOGS", "/Users/Shared/rwm_verify/evidence/R3R0")
os.makedirs(LOGS, exist_ok=True)
OUT = "docs/presubmission/round3/BASELINE_R0.md"
KEYS_OUT = "docs/presubmission/round3/r0_template_keys.txt"


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True).stdout.rstrip("\n")


def run(name, cmd, env=None, rx=None):
    p = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "PY": PY, **(env or {})})
    open(os.path.join(LOGS, name + ".log"), "w").write(p.stdout + p.stderr)
    lines = [l.strip() for l in (p.stdout + p.stderr).splitlines() if l.strip()]
    summ = [l for l in lines if re.search(rx or r"\bPASS\b|\bFAIL|RESULT|criteria met|checks pass|corruptions caught|wrote (PAPER|MODEL|README)", l)]
    if rx: summ = summ[:3]
    return p.returncode, ("; ".join(summ) if rx else (summ[-1] if summ else (lines[-1] if lines else "")))[:300]


status_before = git("status", "--porcelain", "--untracked-files=all")
head = git("rev-parse", "--short", "HEAD")
branch = git("rev-parse", "--abbrev-ref", "HEAD")
rows = []
for s in ("paper_numbers", "build_paper", "build_model_card", "build_readme", "compile_paper"):
    rows.append(("fast build", s + ".py", *run("build_" + s, [PY, f"scripts/{s}.py"])))
compile_log = open(os.path.join(LOGS, "build_compile_paper.log")).read()
GATES = [("ledger_check.py", [], r"RESULT"), ("check_comparative_claims.py", ["--self-test"], r"claims verified|corruptions caught"),
         ("typed_numeral_audit.py", [], r"self-test|typed numerals in|unclassified"), ("restatement_index.py", [], r"\bPASS\b|\bFAIL|typed restatements|ambiguous"),
         ("horizon_sweep.py", [], r"findings"), ("xref_sweep.py", [], r"^\s*(TOTAL|total)|suspect"), ("check_scope_audit.py", [], r"kinds \d+"),
         ("pdf_render_check.py", [], r"PASS")]
for g, a, rx in GATES:
    rows.append(("gate", " ".join([g] + a), *run("gate_" + g[:-3], [PY, f"scripts/{g}", *a], rx=rx)))
name, mail = git("log", "-1", "--format=%an"), git("log", "-1", "--format=%ae")
url = git("remote", "get-url", "origin")
handle = re.sub(r".*github.com[:/]([^/]+)/.*", r"\1", url)
repo_url = re.sub(r"\.git$", "", re.sub(r"^(https://|git@)", "", url).replace(":", "/", 1))
rows.append(("outside the fast build", "part_f_gate.py (identity configured, no CLONE_RESULTS)",
             *run("gate_part_f_gate", [PY, "scripts/part_f_gate.py"], {"RWM_IDENT": f"{name},{mail},{handle}", "RWM_IDENT_REPO": repo_url})))
rows.append(("outside the fast build", "submission_check.py", *run("gate_submission_check", [PY, "scripts/submission_check.py"])))

# C12.1, exactly as the gate computed it in the run above
cc = json.load(open("results/comparative_claims.json"))
c121 = next(c for c in cc["claims"] if c["id"] == "C12.1")
m = re.match(r"(\d+) words \(max (\d+)\), (\d+) numerals \(max (\d+)\) (\[.*\])", c121["detail"])
assert m, c121["detail"]
ab_words, ab_wmax, ab_nums, ab_nmax, ab_list = m.groups()

# restore what the gates rewrote as side effects, then assert the tree is as it was
changed = [l[3:] for l in git("status", "--porcelain").splitlines()]
restored = [f for f in changed if f in ("PAPER.pdf", "results/part_f_gate.json")]
if restored:
    subprocess.run(["git", "checkout", "--", *restored], check=True)
status_after = git("status", "--porcelain", "--untracked-files=all")

# body words, FILE_MAP §13 / round2/t6_words.py
L = open("PAPER.md", encoding="utf-8").read().split("\n")
idx = lambda rx: next(i for i, l in enumerate(L) if re.match(rx, l))
s, d, e = idx(r"^## 1\. Introduction\s*$"), idx(r"^## Data and code\s*$"), idx(r"^## References\s*$")
words = lambda a, b: sum(len(l.split()) for l in L[a:b])
t6 = subprocess.run([PY, "docs/presubmission/round2/t6_words.py"], capture_output=True, text=True).stdout
t6_body = int(re.search(r"body \(Introduction to Data and code\): ([\d,]+)", t6).group(1).replace(",", ""))
assert t6_body == words(s, d), (t6_body, words(s, d))
heads = [(i, l) for i, l in enumerate(L) if re.match(r"^#{2,3} ", l)]
sections = []
for k, (i, l) in enumerate(heads):
    j = heads[k + 1][0] if k + 1 < len(heads) else len(L)
    sections.append((l.strip(), i + 1, words(i, j), i >= s and i < d))
pages = re.search(r"\((\d+) pages", compile_log)

# the template's {{keys}}, for R6/R7's no-result-lost diff
T = open("PAPER.template.md", encoding="utf-8").read()
keys = sorted(set(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", T)))
open(KEYS_OUT, "w").write("\n".join(keys) + "\n")

md = [f"# Round-3 baseline (R0)\n",
      f"Recorded {datetime.date.today().isoformat()} by session R0 on branch `{branch}` at `{head}` "
      f"(`pre-round3` = round 2's final commit `32adcda`, plus R0's commits so far, which touch only `docs/presubmission/round3/`). "
      f"Generated by `docs/presubmission/round3/r0_baseline.py`; logs outside the repository (session evidence folder `R3R0/`).\n",
      "## Length\n",
      "Main text by FILE_MAP §13's rule (whitespace tokens), from `## 1. Introduction`, as "
      "`docs/presubmission/round2/t6_words.py` counts it (its figure is asserted equal to this table's first row):\n",
      "| Cut-point | Words |", "|---|---:|",
      f"| to \"Data and code\" (the line before `## Data and code`; ruling V8's measure) | {words(s, d):,} |",
      f"| to \"References\" (the line before `## References`) | {words(s, e):,} |",
      f"| whole `PAPER.md` | {words(0, len(L)):,} |",
      f"\nRuling V8: at most 20,771 to \"Data and code\" (round 2's final count), aiming for 20,000 or fewer.\n",
      f"**Pages:** {pages.group(1) if pages else 'NOT FOUND'} (`compile_paper.py`).\n",
      "## The abstract, as submission gate C12.1 counts it\n",
      f"- **Words:** {ab_words} (cap {ab_wmax}).",
      f"- **Numerals:** {ab_nums} (cap {ab_nmax}): {ab_list}.",
      f"- Source: `results/comparative_claims.json`, claim C12.1, written by `check_comparative_claims.py` in the gate run below. "
      f"C12.1 counts whitespace tokens between `## Abstract` and `## 1.` of `PAPER.md`, and numerals after removing arXiv identifiers and § references.",
      f"- PLAN R3 item 3 aims for 340 words or fewer.\n",
      "## Template keys\n",
      f"`PAPER.template.md` uses {len(keys):,} distinct `{{{{key}}}}` placeholders; the list is `round3/r0_template_keys.txt` (for Annex 4 item 7's diff).\n",
      "### Per section (`##` and `###` headings of `PAPER.md`, heading line to the line before the next heading)\n",
      "| Heading | PAPER.md line | Words | In the main text |", "|---|---:|---:|---|"]
md += [f"| {h.replace('|', '/')} | {ln} | {w:,} | {'yes' if inb else ''} |" for h, ln, w, inb in sections]
md += ["\n## Gates after one fast build\n",
       "| Kind | Script | Exit | Summary line |", "|---|---|---:|---|"]
md += [f"| {k} | `{n}` | {rc} | {sm.replace('|', '/')} |" for k, n, rc, sm in rows]
md += [f"\nRestored after the gates (side effects, as at S0 and T0): {', '.join('`'+r+'`' for r in restored) or 'none'}. "
       f"Working tree unchanged by the run, apart from `{KEYS_OUT}`: "
       f"{'yes' if [l for l in status_before.splitlines() if KEYS_OUT not in l] == [l for l in status_after.splitlines() if KEYS_OUT not in l] else 'NO'}.\n"]
open(OUT, "w").write("\n".join(md) + "\n")
print(f"wrote {OUT}: body {words(s, d)} to Data and code, {words(s, e)} to References, pages {pages.group(1) if pages else '?'}; "
      f"abstract {ab_words}/{ab_wmax} words, {ab_nums}/{ab_nmax} numerals; keys {len(keys)}")
for r in rows: print(r[0], "|", r[1], "| rc", r[2], "|", r[3])
