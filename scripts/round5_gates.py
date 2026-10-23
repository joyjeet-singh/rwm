"""
Round 5 gates for a short paper (PLAN round 5, G6 item 3). Six checks, each with a corrupt-and-catch self-test.

"Body" is everything from the title to the last line before `## References`, the abstract included.

  pages     main content at most 12 pages, read from the compiled PDF: the page and height at which the References
            heading starts, as round 5's BASELINE_G0 measured it (text block y = 74 to 700 pt).
  abstract  C12.1's count (check_comparative_claims.py, the abstract-budget kind: the text between `## Abstract` and
            `## 1.`, `---` lines removed, arXiv identifiers and § references dropped before counting numerals), at most
            210 words and 5 numerals (ruling Y2).
  ids       no ledger or rule IDs, commit labels, capitalised verdict labels, or code-variable names used as labels in
            the body (ruling Y3); file:line pointers into the released code stay allowed.
  once      in the body of PAPER.template.md, an interval-valued key at most once in prose and at most once in tables
            and captions, and never in the abstract; any other numeric key at most twice across the abstract and the
            body's prose. Keys naming a setting rather than a result are exempt (SETTING_KEY); the exemptions applied
            are listed.
  sig       no decimal with more than two significant figures in the rendered body (PAPER.md), except identifiers,
            version numbers, section, figure, table and equation numbers, and anything in backticks (code).
  keys      every key in docs/presubmission/round5/base_keys.txt is printed by PAPER.template.md or a
            docs/*.template.md, or listed in docs/presubmission/round5/RETIRED_KEYS.md with a reason from its
            vocabulary.

    python scripts/round5_gates.py --report     report every count and never fail (until G16 makes them blocking)
    python scripts/round5_gates.py              fail (exit 1) if any gate fails
    python scripts/round5_gates.py --self-test  the corrupt-and-catch tests only
Writes results/round5_gates.json (not with --self-test).
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import placeholders as PH  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
OUT = os.path.join(ROOT, "results", "round5_gates.json")
R5 = os.path.join(ROOT, "docs", "presubmission", "round5")
MAX_PAGES, MAX_WORDS, MAX_NUMERALS = 12.0, 210, 5
TEXT_TOP, TEXT_BOTTOM = 700.0, 74.0              # BASELINE_G0's text block, pt
RETIRE_VOCAB = ("superseded by key", "a display variant of key", "a restatement removed in favour of key")


# ------------------------------------------------------------------ regions
def body_of(md):
    """Title to the line before `## References`."""
    i = md.find("\n## References")
    return md if i < 0 else md[:i]


def abstract_of(md):
    if "## Abstract" not in md:
        return ""
    return md.split("## Abstract", 1)[1].split("\n## 1.", 1)[0]


# ------------------------------------------------------------------ pages
def pages_from_items(items):
    """items: [(page_index_from_1, text, y)]. The References heading's position -> main-content pages."""
    for p, t, y in items:
        if re.fullmatch(r"(?:\d+\s+)?References", t.strip()):         # LaTeX numbers it ("14 References")
            frac = (TEXT_TOP - y) / (TEXT_TOP - TEXT_BOTTOM)
            return (p - 1) + max(0.0, min(1.0, frac)), {"references_page": p, "references_y": y}
    return None, {"references_page": None}


def pdf_items(path):
    import pypdf
    out = []
    for i, page in enumerate(pypdf.PdfReader(path).pages, 1):
        def visit(text, cm, tm, fd, fs, i=i):
            if text.strip():
                out.append((i, text, tm[5]))
        page.extract_text(visitor_text=visit)
        if any(re.fullmatch(r"(?:\d+\s+)?References", t.strip()) for p, t, y in out if p == i):
            break
    return out


def gate_pages(items):
    p, info = pages_from_items(items)
    return {"pass": p is not None and p <= MAX_PAGES, "value": None if p is None else round(p, 2), "max": MAX_PAGES, **info}


# ------------------------------------------------------------------ abstract
def gate_abstract(md):
    a = abstract_of(md)
    a = re.sub(r"^---\s*$", "", a, flags=re.M)
    words = len(a.split())
    b = re.sub(r"arXiv:\d{4}\.\d{4,5}\w*", "", a)
    b = re.sub(r"§\d+(\.\d+)?", "", b)
    nums = re.findall(r"(?<![\w.])\d[\d,]*\.?\d*(?![\w])", b)
    return {"pass": words <= MAX_WORDS and len(nums) <= MAX_NUMERALS, "words": words, "max_words": MAX_WORDS,
            "numerals": len(nums), "max_numerals": MAX_NUMERALS, "numeral_list": nums}


# ------------------------------------------------------------------ ids
ID_PATTERNS = {
    "ledger_id": r"\b[BCDMORSX]-\d{1,3}\b",
    "rule_id": r"\b(?:X(?:[1-9]|1[0-2])[a-e]?|N(?:[1-9]|1[0-4])|[WY](?:[1-9]|1[0-3]))\b",
    "commit_label": r"\b(?=[0-9a-f]*[a-f])(?=[0-9a-f]*\d)[0-9a-f]{7,40}\b",
}
ACRONYMS = {"RWM", "RWMU", "RWM-U",  # G16: "RWM-U" is the follow-up's name, a false positive logged in OUT_OF_SCOPE since G8
             "MOPO", "PETS", "GRU", "MLP", "RSSM", "CRPS", "NLL", "TMLR", "CPU", "GPU", "PPO", "MBPO", "CSV",
            "PDF", "MSE", "RMS", "RMSE", "ID", "IDS", "AR", "TF", "NB", "URL", "SHA", "API", "README", "MDE", "OOD", "II",
            "III", "IV", "VI", "MLRC", "NEURIPS", "ICLR", "ETH", "NVIDIA", "BSD", "RL", "MPC", "DAD", "TS", "GPS", "CI",
            "IMU", "DOF", "PD", "LSTM", "RNN", "VAE", "KL", "NOT", "AND", "OR", "THE", "BY", "OF", "AT", "IN"}


def verdict_words():
    """Words that appear in the record's capitalised verdict labels (bold runs of capitals in the ledger and the
    protocols), less acronyms. A capitalised run in the body made only of these is a verdict label."""
    src = ""
    for p in ("FINDINGS_LEDGER.md", os.path.join(R5, "PROTOCOLS.md")):
        if os.path.exists(os.path.join(ROOT, p) if not os.path.isabs(p) else p):
            src += open(os.path.join(ROOT, p) if not os.path.isabs(p) else p, encoding="utf-8").read()
    runs = re.findall(r"\*\*([A-Z][A-Z\- ]{3,}[A-Z])\*\*", src)
    words = {w for r in runs for w in re.findall(r"[A-Z][A-Z\-]+", r)}
    return sorted(w for w in words - ACRONYMS if len(w) >= 4)


def gate_ids(md, vwords):
    body = body_of(md)
    nocode = re.sub(r"`[^`]*\.(?:py|json|yaml|md|csv|pt)(?::[\d,-]+)?`", " ", body)     # file:line pointers allowed
    hits = {}
    for name, pat in ID_PATTERNS.items():
        hits[name] = sorted(set(re.findall(pat, nocode)))
    vw = set(vwords)
    caps = re.findall(r"\b[A-Z][A-Z\-]{3,}(?:\s+[A-Z][A-Z\-]{1,})*\b", nocode)
    hits["verdict_label"] = sorted({c for c in caps if all(w in vw or w in {"NOT", "THE", "OF", "AT", "IN", "BY", "AND"}
                                                           for w in c.split()) and any(w in vw for w in c.split())})
    hits["code_label"] = sorted(set(re.findall(r"`([a-z]+(?:-[a-z]+)+)`", nocode)))
    counts = {k: sum(len(re.findall(re.escape(x) if k in ("verdict_label", "code_label") else
                                    r"\b" + re.escape(x) + r"\b", nocode)) for x in v) for k, v in hits.items()}
    n = sum(counts.values())
    return {"pass": n == 0, "n": n, "by_kind": counts, "distinct": hits}


# ------------------------------------------------------------------ once
SETTING_KEY = re.compile(r"(?:^|_)(?:h|deploy_h|diag_h)$|iters|_iter|(?:^|_)n_?(?:traj|ind|nind|independent|episodes?|eps|units|"
                         r"runs|seeds?|boot|cells|dims?|configs|folds|members|draws)|_nind|(?:^|_)nind|seeds?$|_n$|^n_entries|"
                         r"ledger_kb|_word$|_word_|_words?$|(?:^|_)k$|_len$|_dt$|window")


def is_interval(v):
    s = str(v)
    return bool(re.search(r"\[[^\]]*\d[^\]]*,[^\]]*\d[^\]]*\]", s) or "±" in s)


def is_numeric(v):
    return bool(re.search(r"\d", str(v)))


def classify_lines(text):
    """Each line of `text` as 'table', 'caption' or 'prose'. Tables: lines starting with '|'. Captions: a line in
    italics (starting and ending with '*') or starting 'Figure '/'Table ', within three lines after a table."""
    lines = text.split("\n")
    kinds, last_table = [], -10
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s.startswith("|"):
            kinds.append("table")
            last_table = i
        elif (s.startswith("*") and s.endswith("*") and len(s) > 2) or re.match(r"\*{0,2}(Figure|Table) \d", s):
            kinds.append("caption" if i - last_table <= 3 or re.match(r"\*{0,2}(Figure|Table) \d", s) else "prose")
        else:
            kinds.append("prose")
    return lines, kinds


def gate_once(tpl, N):
    body = body_of(tpl)
    abstract = abstract_of(body)
    lines, kinds = classify_lines(body)
    a0 = body.find("## Abstract")
    a1 = a0 + len("## Abstract") + len(abstract) if a0 >= 0 else -1
    pos, where = 0, {}
    for ln, kd in zip(lines, kinds):
        in_abs = a0 <= pos < a1
        for m in PH.PH.finditer(ln):
            k = m.group(1)
            if k not in N or not is_numeric(N[k]["value"]):
                continue
            w = where.setdefault(k, {"abstract": 0, "prose": 0, "table_caption": 0})
            w["abstract" if in_abs else ("prose" if kd == "prose" else "table_caption")] += 1
        pos += len(ln) + 1
    viol, exempt = [], []
    for k, w in sorted(where.items()):
        if SETTING_KEY.search(k):
            if sum(w.values()) > 2:
                exempt.append(k)
            continue
        if is_interval(N[k]["value"]):
            if w["abstract"] > 0 or w["prose"] > 1 or w["table_caption"] > 1:
                viol.append({"key": k, "interval": True, **w})
        elif w["abstract"] + w["prose"] > 2:
            viol.append({"key": k, "interval": False, **w})
    return {"pass": not viol, "n": len(viol), "violations": viol, "exempt_setting_keys_applied": exempt}


# ------------------------------------------------------------------ sig
SIG_EXCEPT = [("arXiv-style identifier", r"\b\d{4}\.\d{4,5}\b"), ("version number", r"\b\d+\.\d+\.\d+(?:\.\d+)*\b"),
              ("section, figure, table or equation number",
               r"(?:§|Section |Appendix |Figure |Table |Eq\. |Equation |Step |Session )\d+(?:\.\d+)+"),
              ("code, in backticks", r"`[^`]*`"), ("URL", r"https?://\S+")]


def sig_figs(tok):
    digits = tok.replace(",", "").replace(".", "").lstrip("+-−").lstrip("0")
    return len(digits)


def gate_sig(md):
    body = body_of(md)
    masked = body
    for _, pat in SIG_EXCEPT:
        masked = re.sub(pat, lambda m: " " * len(m.group(0)), masked)
    toks = re.findall(r"(?<![\w.])\d[\d,]*\.\d+(?![\w]|\.\d)", masked)
    bad = [t for t in toks if sig_figs(t) > 2]
    return {"pass": not bad, "n": len(bad), "n_decimals": len(toks), "examples": bad[:25],
            "exceptions": [name for name, _ in SIG_EXCEPT]}


# ------------------------------------------------------------------ keys
def printed_keys():
    ks = set()
    for p in ["PAPER.template.md"] + sorted(glob.glob(os.path.join(ROOT, "docs", "*.template.md"))):
        ks |= {m.group(1) for m in PH.PH.finditer(open(os.path.join(ROOT, p) if not os.path.isabs(p) else p).read())}
    return ks - {"FIGURES"}


def retired_keys(text):
    out, bad = {}, []
    for m in re.finditer(r"^\|\s*`?([A-Za-z0-9_]+)`?\s*\|\s*([^|]+?)\s*\|", text, re.M):
        k, why = m.group(1), m.group(2)
        if k in ("Key",) or set(k) <= {"-"}:
            continue
        if any(why.lower().startswith(v) for v in RETIRE_VOCAB):
            out[k] = why
        else:
            bad.append({"key": k, "reason": why})
    return out, bad


def gate_keys(base, printed, retired_text):
    retired, bad_reason = retired_keys(retired_text)
    missing = sorted(set(base) - printed - set(retired))
    return {"pass": not missing and not bad_reason, "missing": missing, "n_missing": len(missing), "n_base": len(base),
            "n_retired": len(retired), "retired_with_bad_reason": bad_reason}


# ------------------------------------------------------------------ self-test
def self_test():
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)
    check("pages: 11.5 passes", gate_pages([(12, "References", 387.0)])["pass"])
    check("pages: 13.2 fails", not gate_pages([(14, "References", 575.0)])["pass"])
    check("pages: a numbered heading is found", gate_pages([(12, "14 References", 387.0)])["value"] is not None)
    check("pages: no References heading fails", not gate_pages([(3, "Intro", 500.0)])["pass"])
    short = "# T\n\n## Abstract\n\nWe test 3 claims.\n\n## 1. Intro\n"
    check("abstract: short passes", gate_abstract(short)["pass"])
    check("abstract: 6 numerals fail", not gate_abstract(short.replace("3 claims", "1 2 3 4 5 6 claims"))["pass"])
    check("abstract: 211 words fail", not gate_abstract(short.replace("We test", "word " * 211))["pass"])
    vw = ["PARTIAL", "SUPPORTED", "GENERALISES", "MECHANISM"]
    check("ids: clean passes", gate_ids("# T\n\nThe result holds at `system_dynamics.py:115`.\n## References\n", vw)["pass"])
    for plant in ("rule M-43 says", "as X9 found", "commit 9a46560 shows", "it returns MECHANISM SUPPORTED here",
                  "the `entry-res` baseline", "verdict PARTIAL"):
        check(f"ids: catches {plant!r}", not gate_ids(f"# T\n\nText {plant}.\n## References\n", vw)["pass"])
    check("ids: after References is not body", gate_ids("# T\n\nok.\n## References\n\nM-43\n", vw)["pass"])
    N = {"ci": {"value": "[0.69, 0.82]"}, "r": {"value": "0.75"}, "h": {"value": "100"}, "v2_deploy_h": {"value": "100"}}
    ok_t = "# T\n## Abstract\nAbout {{r}}.\n## 1. A\nThe ratio is {{ci}} and {{r}}.\n\n| a | {{ci}} |\n## References\n"
    check("once: clean passes", gate_once(ok_t, N)["pass"])
    check("once: interval in abstract fails", not gate_once(ok_t.replace("About {{r}}", "About {{ci}}"), N)["pass"])
    check("once: interval twice in prose fails", not gate_once(ok_t.replace("and {{r}}", "and {{ci}}"), N)["pass"])
    check("once: numeric key three times fails", not gate_once(ok_t + "Again {{r}}.\n", N)["pass"] or
          not gate_once(ok_t.replace("## References", "Again {{r}}.\n## References"), N)["pass"])
    check("once: setting key exempt",
          gate_once(ok_t.replace("## References", "{{v2_deploy_h}} {{v2_deploy_h}} {{v2_deploy_h}}\n## References"), N)["pass"])
    check("sig: two figures pass", gate_sig("# T\n\nIt is 0.75 and 33 and §6.2 and arXiv 2501.10100 and torch 2.2.2.\n## References\n")["pass"])
    check("sig: three figures fail", not gate_sig("# T\n\nIt is 0.753.\n## References\n")["pass"])
    check("sig: backticked code exempt", gate_sig("# T\n\nThe value `0.753` in code.\n## References\n")["pass"])
    rt = "| Key | Reason | Session |\n|---|---|---|\n| `old_key` | superseded by key new_key | G9 |\n"
    check("keys: printed or retired passes", gate_keys(["a", "old_key"], {"a"}, rt)["pass"])
    check("keys: a dropped key fails", not gate_keys(["a", "b"], {"a"}, rt)["pass"])
    check("keys: a bad reason fails", not gate_keys(["a", "x"], {"a"}, rt.replace("old_key", "x").replace(
        "superseded by key new_key", "not needed"))["pass"])
    check("placeholders: sN recognised", PH.PH.fullmatch("{{r|s2}}") is not None)
    return fails


def main():
    os.chdir(ROOT)
    fails = self_test()
    print(f"  self-test: {'PASS' if not fails else 'FAIL ' + str(fails)}")
    if "--self-test" in sys.argv:
        return 0 if not fails else 1
    if fails:
        print("  the gates are not run: a gate that cannot fail proves nothing")
        return 1
    N = json.load(open(os.path.join(ROOT, "results", "paper_numbers.json")))
    md, tpl = open("PAPER.md").read(), open("PAPER.template.md").read()
    base = [k.strip() for k in open(os.path.join(R5, "base_keys.txt")) if k.strip()]
    retired = open(os.path.join(R5, "RETIRED_KEYS.md")).read()
    vw = verdict_words()
    G = {"pages": gate_pages(pdf_items("PAPER.pdf")), "abstract": gate_abstract(md), "ids": gate_ids(md, vw),
         "once": gate_once(tpl, N), "sig": gate_sig(md), "keys": gate_keys(base, printed_keys(), retired)}
    G["ids"]["verdict_vocabulary"] = vw
    line = (f"pages {G['pages']['value']}/{int(MAX_PAGES)}, abstract {G['abstract']['words']}/{G['abstract']['numerals']}, "
            f"ids {G['ids']['n']}, once {G['once']['n']}, sig {G['sig']['n']}, keys missing {G['keys']['n_missing']}")
    for k, v in G.items():
        print(f"  {k:<9} {'pass' if v['pass'] else 'FAIL'}")
    print(f"  round-5 gates: {line}")
    json.dump({"mode": "report" if "--report" in sys.argv else "blocking", "summary": line, "gates": G},
              open(OUT, "w"), indent=1)
    print(f"  wrote results/round5_gates.json")
    if "--report" in sys.argv:
        return 0
    return 0 if all(v["pass"] for v in G.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
