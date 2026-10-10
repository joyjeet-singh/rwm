"""F0 item 4: the round-4 baselines, written to docs/presubmission/round4/BASELINE_F0.md.

Round 3's r0_baseline.py, adapted. One fast build (FILE_MAP §3), then every gate, then the two gates
outside the fast build (part_f_gate with the identity configured and no clone, and submission_check),
each recorded as exit code plus its summary line. Then:
  - main-text words by docs/presubmission/round2/t6_words.py (FILE_MAP §13: whitespace tokens, str.split(),
    from `## 1. Introduction` to the line before `## Data and code`), in total and per `##`/`###` section;
  - the page count, from compile_paper.py's own output, and the page on which References starts, from the
    built PAPER.pdf's text (pypdf), asserted equal for the committed PAPER.pdf;
  - the abstract's word and numeral counts and caps exactly as submission gate C12.1 computes them
    (read from results/comparative_claims.json, which check_comparative_claims.py writes);
  - a count of ledger IDs in the main text, by kind, plus rule labels X1..X8 and commit labels (hex tokens
    that are commits of this repository, by docs/COMMIT_LABEL_MAP.json or `git rev-parse`), per section;
  - the set of {{keys}} PAPER.template.md uses, written to round4/f0_template_keys.txt (PLAN Annex 6 item 4).
Every figure is read from what the scripts print or from PAPER.md; none is typed. Tracked files that a
gate rewrites as a side effect (PAPER.pdf's timestamps, results/part_f_gate.json) are restored afterwards,
and the tree is asserted unchanged. Logs go to $F0_LOGS (outside the repository).
Run from the repository root:  $PY docs/presubmission/round4/f0_baseline.py
"""
import collections, datetime, json, os, re, subprocess, sys

import pypdf

PY = sys.executable
LOGS = os.environ.get("F0_LOGS", "/Users/Shared/rwm_verify/evidence/R4F0")
os.makedirs(LOGS, exist_ok=True)
OUT = "docs/presubmission/round4/BASELINE_F0.md"
KEYS_OUT = "docs/presubmission/round4/f0_template_keys.txt"


def git(*a):
    return subprocess.run(["git", *a], capture_output=True, text=True).stdout.rstrip("\n")


def run(name, cmd, env=None, rx=None):
    p = subprocess.run(cmd, capture_output=True, text=True, env={**os.environ, "PY": PY, **(env or {})})
    open(os.path.join(LOGS, name + ".log"), "w").write(p.stdout + p.stderr)
    lines = [l.strip() for l in (p.stdout + p.stderr).splitlines() if l.strip()]
    summ = [l for l in lines if re.search(rx or r"\bPASS\b|\bFAIL|RESULT|criteria met|checks pass|corruptions caught|wrote (PAPER|MODEL|README)", l)]
    if rx: summ = summ[:3]
    return p.returncode, ("; ".join(summ) if rx else (summ[-1] if summ else (lines[-1] if lines else "")))[:300]


def references_page(pdf):
    """1-based page of the first line reading '<n> References' (or 'References'), and of 'Data and code'."""
    found = {}
    for i, pg in enumerate(pypdf.PdfReader(pdf).pages):
        for l in (pg.extract_text() or "").split("\n"):
            for key, rx in (("references", r"^\s*(\d+\s*)?References\s*$"), ("data", r"^\s*(\d+\s*)?Data\s*and\s*code\s*$")):
                if key not in found and re.match(rx, l):
                    found[key] = i + 1
    return found, len(pypdf.PdfReader(pdf).pages)


status_before = git("status", "--porcelain", "--untracked-files=all")
head = git("rev-parse", "--short", "HEAD")
branch = git("rev-parse", "--abbrev-ref", "HEAD")
rows = []
for s in ("paper_numbers", "build_paper", "build_model_card", "build_readme", "compile_paper"):
    rows.append(("fast build", s + ".py", *run("build_" + s, [PY, f"scripts/{s}.py"])))
compile_log = open(os.path.join(LOGS, "build_compile_paper.log")).read()
built_changed = [l[3:] for l in git("status", "--porcelain").splitlines()
                if not l.startswith("??") and l not in status_before.splitlines()]
built_pages, built_npages = references_page("PAPER.pdf")
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
rows.append(("outside the fast build", "submission_check.py",
             *run("gate_submission_check", [PY, "scripts/submission_check.py"], rx=r"criteria met|outstanding:")))

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
committed_pages, committed_npages = references_page("PAPER.pdf")
assert (built_pages, built_npages) == (committed_pages, committed_npages), (built_pages, built_npages, committed_pages, committed_npages)

# body words, FILE_MAP §13 / round2/t6_words.py
L = open("PAPER.md", encoding="utf-8").read().split("\n")
idx = lambda rx: next(i for i, l in enumerate(L) if re.match(rx, l))
s, d, e = idx(r"^## 1\. Introduction\s*$"), idx(r"^## Data and code\s*$"), idx(r"^## References\s*$")
ab = idx(r"^## Abstract\s*$")
words = lambda a, b: sum(len(l.split()) for l in L[a:b])
t6 = subprocess.run([PY, "docs/presubmission/round2/t6_words.py"], capture_output=True, text=True).stdout
t6_body = int(re.search(r"body \(Introduction to Data and code\): ([\d,]+)", t6).group(1).replace(",", ""))
assert t6_body == words(s, d), (t6_body, words(s, d))
heads = [(i, l) for i, l in enumerate(L) if re.match(r"^#{2,3} ", l)]
sections = []
for k, (i, l) in enumerate(heads):
    j = heads[k + 1][0] if k + 1 < len(heads) else len(L)
    sections.append((l.strip(), i + 1, j, words(i, j), s <= i < d))
pages = re.search(r"\((\d+) pages", compile_log)
assert pages and int(pages.group(1)) == built_npages, (pages and pages.group(1), built_npages)

# ledger IDs, rule labels and commit labels in the text
LEDGER = open("FINDINGS_LEDGER.md", encoding="utf-8").read()
ledger_ids = set(re.findall(r"^#{2,4} ([A-Z]-\d+)\b", LEDGER, flags=re.M))
KINDS = sorted({x.split("-")[0] for x in ledger_ids})
labels = json.load(open("docs/COMMIT_LABEL_MAP.json"))["labels"]
_commit_cache = {}


def commit_kind(tok):
    """'ours' if tok is a prefix of a commit in COMMIT_LABEL_MAP or resolves in this repository; else None."""
    if tok not in _commit_cache:
        hit = [v for k, v in labels.items() if k.startswith(tok)]
        if not hit and git("rev-parse", "--verify", "--quiet", tok + "^{commit}"):
            hit = ["(resolves by git rev-parse; not in the label map)"]
        _commit_cache[tok] = hit[0] if hit else None
    return _commit_cache[tok]


def id_counts(a, b):
    text = "\n".join(L[a:b])
    c = collections.Counter()
    unresolved, hexother = set(), set()
    for mm in re.finditer(r"(?<![A-Za-z0-9_§])([A-Z])-(\d+)\b", text):
        k, ident = mm.group(1), f"{mm.group(1)}-{mm.group(2)}"
        if k in KINDS:
            c[k + "-"] += 1
            if ident not in ledger_ids:
                unresolved.add(ident)
    c["X1..X8 (rule labels)"] = len(re.findall(r"(?<![A-Za-z0-9_-])X[1-8]\b", text))
    for mm in re.finditer(r"(?<![0-9A-Za-z_])([0-9a-f]{7,40})(?![0-9A-Za-z_])", text):
        tok = mm.group(1)
        mixed = bool(re.search(r"[a-f]", tok) and re.search(r"[0-9]", tok))
        in_map = any(k.startswith(tok) for k in labels)
        if not (mixed or in_map):
            continue
        if commit_kind(tok):
            c["commit labels"] += 1
        else:
            hexother.add(tok)
    return c, unresolved, hexother


COLS = [k + "-" for k in KINDS] + ["X1..X8 (rule labels)", "commit labels"]
front_c, front_u, front_h = id_counts(0, s)
body_c, body_u, body_h = id_counts(s, d)
dc_c, dc_u, dc_h = id_counts(d, e)
sec_counts = [(h, ln, id_counts(ln - 1, j)[0]) for h, ln, j, w, inb in sections if inb]

# the template's {{keys}}, for F10's no-result-lost diff
T = open("PAPER.template.md", encoding="utf-8").read()
keys = sorted(set(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", T)))
open(KEYS_OUT, "w").write("\n".join(keys) + "\n")

md = [f"# Round-4 baseline (F0)\n",
      f"Recorded {datetime.date.today().isoformat()} by session F0 on branch `{branch}` at `{head}` "
      f"(`pre-round4` = round 3's final commit `{git('rev-parse', '--short', 'pre-round4')}`, plus F0's commits so far, which touch only "
      f"`docs/presubmission/round4/`). Generated by `docs/presubmission/round4/f0_baseline.py`; logs outside the repository "
      f"(session evidence folder `R4F0/`).\n",
      "## Length\n",
      "Main text by FILE_MAP §13's rule (whitespace tokens), from `## 1. Introduction`, as "
      "`docs/presubmission/round2/t6_words.py` counts it (its figure is asserted equal to this table's first row):\n",
      "| Cut-point | Words |", "|---|---:|",
      f"| to \"Data and code\" (the line before `## Data and code`; ruling W6's measure) | {words(s, d):,} |",
      f"| to \"References\" (the line before `## References`) | {words(s, e):,} |",
      f"| whole `PAPER.md` | {words(0, len(L)):,} |",
      f"\nRuling W6: at most 16,000 to \"Data and code\", aiming for 15,000, by moving text and never deleting it.\n",
      f"**Pages:** {pages.group(1)} (`compile_paper.py`; equal to the built PDF's page count).  ",
      f"**References starts on page {built_pages.get('references')}**, so the page before References is {built_pages.get('references') - 1}; "
      f"\"Data and code\" starts on page {built_pages.get('data')}. (The first PDF line reading \"References\" or \"Data and code\", "
      f"optionally after its section number, by `pypdf` text extraction; the same for the committed and the rebuilt `PAPER.pdf`.)\n",
      "## The abstract, as submission gate C12.1 counts it\n",
      f"- **Words:** {ab_words} (cap {ab_wmax}).",
      f"- **Numerals:** {ab_nums} (cap {ab_nmax}): {ab_list}.",
      f"- Source: `results/comparative_claims.json`, claim C12.1, written by `check_comparative_claims.py` in the gate run below. "
      f"C12.1 counts whitespace tokens between `## Abstract` and `## 1.` of `PAPER.md`, and numerals after removing arXiv identifiers and § references.",
      f"- Ruling W7: at most 300 words; F6 tightens C12.1's word cap from {ab_wmax} to 320.\n",
      "## Internal labels in the text (ruling W8)\n",
      f"Counted in `PAPER.md`. Ledger IDs are `<kind>-<n>` for every kind the ledger's headings use ({', '.join(k + '-' for k in KINDS)}); "
      f"\"X1..X8\" are the round-3/4 rule labels (written without a hyphen); a commit label is a 7–40-character hex token that is a commit of this "
      f"repository (by `docs/COMMIT_LABEL_MAP.json`, or `git rev-parse`). Each occurrence counts once.\n",
      "| Region | " + " | ".join(COLS) + " | all |", "|---|" + "---:|" * (len(COLS) + 1)]
for lab, c in (("front matter (title to the line before `## 1. Introduction`)", front_c), ("**main text** (`## 1. Introduction` to the line before `## Data and code`)", body_c),
               ("\"Data and code\" (to the line before `## References`)", dc_c)):
    md.append(f"| {lab} | " + " | ".join(str(c[k]) for k in COLS) + f" | {sum(c[k] for k in COLS)} |")
md += ["",
       f"IDs of a ledger kind that match no ledger heading: front matter {sorted(front_u) or 'none'}; main text {sorted(body_u) or 'none'}; \"Data and code\" {sorted(dc_u) or 'none'}.  ",
       f"Hex tokens with letters and digits that are not commits of this repository (upstream pins and other identifiers, not counted): "
       f"front matter {sorted(front_h) or 'none'}; main text {sorted(body_h) or 'none'}; \"Data and code\" {sorted(dc_h) or 'none'}.\n",
       "Per main-text section (sections with no label omitted):\n",
       "| Heading | PAPER.md line | " + " | ".join(COLS) + " |", "|---|---:|" + "---:|" * len(COLS)]
md += [f"| {h.replace('|', '/')} | {ln} | " + " | ".join(str(c[k]) for k in COLS) + " |" for h, ln, c in sec_counts if sum(c[k] for k in COLS)]
md += ["", "## Template keys\n",
       f"`PAPER.template.md` uses {len(keys):,} distinct `{{{{key}}}}` placeholders; the list is `round4/f0_template_keys.txt` (for Annex 6 item 4's diff).\n",
       "## Words per section (`##` and `###` headings of `PAPER.md`, heading line to the line before the next heading)\n",
       "| Heading | PAPER.md line | Words | In the main text |", "|---|---:|---:|---|"]
md += [f"| {h.replace('|', '/')} | {ln} | {w:,} | {'yes' if inb else ''} |" for h, ln, j, w, inb in sections]
md += ["\n## Gates after one fast build\n",
       "| Kind | Script | Exit | Summary line |", "|---|---|---:|---|"]
md += [f"| {k} | `{n}` | {rc} | {sm.replace('|', '/')} |" for k, n, rc, sm in rows]
md += [f"\nTracked files the fast build changed: {', '.join('`'+x+'`' for x in built_changed) or 'none'}. "
       f"`submission_check`'s outstanding criterion is C1, the claims audit, left unreviewed by round 2's ruling U5 "
       f"(`docs/presubmission/round2/DECISIONS.md:{next(i + 1 for i, l in enumerate(open('docs/presubmission/round2/DECISIONS.md')) if l.startswith('| U5 |'))}`), "
       f"as at R0 and in round 3's final verification. "
       f"Restored after the gates (side effects, as at S0, T0 and R0): {', '.join('`'+r+'`' for r in restored) or 'none'}. "
       f"Working tree unchanged by the run, apart from `{KEYS_OUT}`: "
       f"{'yes' if [l for l in status_before.splitlines() if KEYS_OUT not in l] == [l for l in status_after.splitlines() if KEYS_OUT not in l] else 'NO'}.\n"]
open(OUT, "w").write("\n".join(md) + "\n")
print(f"wrote {OUT}: body {words(s, d)} to Data and code, {words(s, e)} to References, pages {pages.group(1)}, References p{built_pages.get('references')}; "
      f"abstract {ab_words}/{ab_wmax} words, {ab_nums}/{ab_nmax} numerals; keys {len(keys)}; main-text IDs {dict(body_c)}")
for r in rows: print(r[0], "|", r[1], "| rc", r[2], "|", r[3])
