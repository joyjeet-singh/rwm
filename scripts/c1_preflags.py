"""
Build the C1 review queue: one tier and a set of advisory pre-flags per claim.

This does the machine-checkable half of the review protocol's four questions so
the human can spend their attention on the half no machine can do. It assigns no
verdict and it approves nothing.

TIERS. The protocol defines three tiers that OVERLAP -- Tier 1 is "the Part A and
B claims", Tier 2 "the 33 changed", Tier 3 "the 53 new" -- and the Part A/B
claims are drawn from the other two. Implemented literally the human reviews some
claims twice and may believe a tier is finished when it is not. Each claim gets
exactly one tier here, by precedence:

  1  text added or changed by the Part A / Part B commits, identified from the
     commit range rather than by guessing at subject matter
  2  a value, horizon, count or hedge changed against the last reviewed text
  3  a genuinely new sentence
  4  wording only

PRE-FLAGS ARE ADVISORY AND NEVER VERDICTS. A clean claim is not pre-approved and
goes through the same expectation-then-reveal as any other; a flagged claim is
not pre-rejected. They exist to say where to slow down.

Writes results/c1_review_queue.json.
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402
import horizon_sweep as HS  # noqa: E402

TEMPLATE = "PAPER.template.md"
OUT = os.path.join(R.RESULTS, "c1_review_queue.json")

# The commits whose prose is Tier 1. Named by subject, not by hash, because a
# history rewrite moves hashes and this project has already had one (M-48).
TIER1_SUBJECTS = (
    "Part A: the A/B result is a curve, and h=368 is the end of a trend",
    "Part B: the h=100 consequences, and the frequency claims nobody was checking",
)

STRENGTH_VERBS = ("establishes", "establish", "established", "shows", "show",
                  "proves", "prove", "proven", "demonstrates", "demonstrate",
                  "confirms", "confirm", "confirmed")
FREQUENCY_WORDS = ("exactly", "only", "never", "all four", "the only",
                   "every one", "at every", "in all", "none of")
# Keys whose VALUE is a horizon rather than a result. Two of them printing the
# same number is the grid working, not an ambiguity.
HORIZON_KEYS = {"v2_deploy_h", "v2_diag_h", "d3_worst_h", "d3_second_h",
                "r2_sigma_x_lo_h", "r2_sigma_x_hi_h", "e5_power_worst_h",
                "d2p_narrowest_h", "d1_rule_h", "perm_worst_h"}
ARENA_WORDS = ("out-of-sample", "in-sample", "held-out", "all ten episodes",
               "held out", "n_independent", "arena")


def tier1_lines():
    """Every line the Part A / Part B commits ADDED to the template.

    Identified from the commit range, per the brief. Subject lookup rather than
    hash so a rewrite cannot silently empty this set -- which would demote the
    newest prose in the paper to Tier 3 and lose the reason it is Tier 1.
    """
    out = set()
    log = subprocess.run(["git", "log", "--format=%H\t%s"],
                         capture_output=True, text=True).stdout
    by_subject = {s: h for h, _, s in (ln.partition("\t") for ln in log.splitlines())}
    for subj in TIER1_SUBJECTS:
        h = by_subject.get(subj)
        assert h, f"no commit with subject {subj!r}; Tier 1 would be silently empty"
        d = subprocess.run(["git", "show", "--format=", "-U0", h, "--", TEMPLATE],
                           capture_output=True, text=True).stdout
        for ln in d.splitlines():
            if ln.startswith("+") and not ln.startswith("+++"):
                t = ln[1:].strip()
                if len(t) > 24:
                    out.add(HS._resolve(t) if "{{" in t else t)
    return out


def key_meta():
    """For every paper_numbers key: its horizon, arena and n_independent.

    Read from the artifact each key is sourced from, so a flag about arena or
    sample size is grounded in what produced the number rather than in the key's
    name.
    """
    N = json.load(open(os.path.join(R.RESULTS, "paper_numbers.json")))
    grid = HS.horizon_grid()
    cache, meta = {}, {}
    for k, v in N.items():
        src = str(v.get("source", ""))
        arena = nind = None
        for fn in re.findall(r"results/([\w.]+\.json)", src):
            if fn not in cache:
                p = os.path.join(R.RESULTS, fn)
                try:
                    cache[fn] = json.load(open(p))
                except Exception:                                  # noqa: BLE001
                    cache[fn] = {}
            d = cache[fn].get("design", {}) if isinstance(cache[fn], dict) else {}
            arena = arena or d.get("arena")
            nind = nind if nind is not None else d.get("n_independent")
        meta[k] = {"horizon": HS.key_horizon(k, grid), "arena": arena,
                   "n_independent": nind, "source": src,
                   "value": str(v.get("value"))}
    return meta


def paragraphs(text):
    """(line_no, paragraph) for every prose block, so a claim can find its own."""
    out, buf, start, in_code = [], [], 1, False
    for n, ln in enumerate(text.split("\n"), 1):
        if ln.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if not ln.strip():
            if buf:
                out.append((start, " ".join(buf)))
                buf = []
            continue
        if not buf:
            start = n
        buf.append(ln.strip())
    if buf:
        out.append((start, " ".join(buf)))
    return out


def main():
    audit = json.load(open(os.path.join(R.RESULTS, "task_c1_claims_audit.json")))
    diff = json.load(open(os.path.join(R.RESULTS, "c1_diff_report.json")))
    diff_by_id = {r["id"]: r for r in diff["rows"]}
    tpl = open(TEMPLATE).read()
    paras = paragraphs(tpl)
    meta = key_meta()
    grid = HS.horizon_grid()
    deploy, diag = HS.deploy_diag()
    t1 = tier1_lines()
    used_keys = set(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", tpl))

    un = [c for c in audit["claims"] if c["verdict"] == "UNREVIEWED"]
    rows = []
    for c in un:
        claim = c["claim"]
        keys = re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", claim)
        # the paragraph this claim sits in, for context and for paragraph-scope flags
        para, para_line = "", None
        best = 0
        for ln, p in paras:
            frag = claim[:70]
            if frag and frag in p and len(p) > best:
                para, para_line, best = p, ln, len(p)
        if not para:
            para, para_line = claim, None

        # ---- tier -------------------------------------------------------
        rendered = HS._resolve(claim)
        in_t1 = any(rendered[:60] in ln or ln[:60] in rendered for ln in t1 if ln)
        d = diff_by_id.get(c["id"], {})
        reasons = d.get("reasons", [])
        is_new = any("no earlier text found" in r for r in reasons)
        if in_t1:
            tier, why = 1, "text added or changed by the Part A / Part B commits"
        elif reasons and not is_new:
            tier, why = 2, "; ".join(reasons)[:200]
        elif is_new:
            tier, why = 3, "a genuinely new sentence, never reviewed"
        else:
            tier, why = 4, "wording only"

        # ---- pre-flags --------------------------------------------------
        flags, r_amb = [], None
        hz = {meta[k]["horizon"] for k in keys if k in meta and meta[k]["horizon"]}
        named_s = HS.named_horizons(claim, deploy, diag, grid)
        named_p = HS.named_horizons(para, deploy, diag, grid)
        if hz and not (hz & named_s):
            flags.append("missing-horizon")
        arenas = {meta[k]["arena"] for k in keys if k in meta and meta[k]["arena"]}
        if arenas and not any(w in para.lower() for w in ARENA_WORDS):
            flags.append("missing-arena")
        nn = [meta[k]["n_independent"] for k in keys
              if k in meta and meta[k]["n_independent"] is not None]
        if nn and min(nn) <= 4 and any(v in claim.lower() for v in STRENGTH_VERBS):
            flags.append("strength-vs-n")
        para_hz = set()
        for k in re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", para):
            h = meta.get(k, {}).get("horizon")
            if h:
                para_hz.add(h)
        if len(para_hz) >= 2:
            flags.append("mixed-horizon-para")
        for k in keys:
            val = meta.get(k, {}).get("value")
            if not val or len(val) < 3:
                continue
            # The same printed numeral reached by a DIFFERENT key is the shape
            # that makes a sentence look verified when it is not: a reader (and
            # a reviewer) matches the numeral, not the provenance.
            #
            # The first version of this asked whether "{{j}}" appeared in the
            # RESOLVED paper, where placeholders no longer exist -- so it could
            # never fire, and reported zero while seven duplicate values sat in
            # the queue including the 4.61 collision the previous review named.
            # An assertion that cannot fire is the failure mode appendix D
            # already records twice. Compare against keys actually USED in the
            # template instead.
            # ...but only for RESULT numerals. Horizon labels collide by
            # construction -- v2_deploy_h and d3_worst_h both print "100" and
            # always will -- and a flag that fires on two thirds of the queue
            # trains the reader to skip it, which is worse than not having it.
            # The case worth stopping on is the one the previous review named:
            # 4.61 as an A/B ratio and 4.61% as a coverage, three sentences
            # apart and meaning nothing alike.
            if val.replace(",", "").isdigit() and int(val.replace(",", "")) in grid:
                continue
            if k in HORIZON_KEYS:
                continue
            twins = sorted(j for j in used_keys
                           if j != k and j not in HORIZON_KEYS
                           and meta.get(j, {}).get("value") == val)
            if twins:
                flags.append("ambiguous-numeral")
                r_amb = {"value": val, "key": k, "also_reached_by": twins[:4]}
                break
        if any(w in claim.lower() for w in FREQUENCY_WORDS):
            flags.append("frequency-word")
        if "ambiguous-numeral" not in flags:
            r_amb = None

        rows.append({
            "id": c["id"], "section": c["section"], "tier": tier, "tier_reason": why,
            "claim": claim, "paragraph": para, "paragraph_line": para_line,
            "keys": keys, "flags": sorted(set(flags)),
            "registered": {k: meta[k] for k in keys if k in meta},
            "ambiguous_numeral_detail": r_amb,
            "previous_text": d.get("previous"),
        })

    rows.sort(key=lambda r: (r["tier"], r["section"], r["id"]))
    counts = {t: sum(1 for r in rows if r["tier"] == t) for t in (1, 2, 3, 4)}
    fl = {}
    for r in rows:
        for f in r["flags"]:
            fl[f] = fl.get(f, 0) + 1
    out = {"n_claims": len(rows), "tier_counts": counts,
           "n_with_any_flag": sum(1 for r in rows if r["flags"]),
           "flag_counts": dict(sorted(fl.items(), key=lambda x: -x[1])),
           "tier1_commits": list(TIER1_SUBJECTS), "claims": rows}
    json.dump(out, open(OUT, "w"), indent=2)

    print("C1 REVIEW QUEUE — tiers and advisory pre-flags")
    print("=" * 96)
    print(f"  claims awaiting review : {len(rows)}")
    print(f"  tier 1 (Part A / B)    : {counts[1]}")
    print(f"  tier 2 (something changed): {counts[2]}")
    print(f"  tier 3 (new sentence)  : {counts[3]}")
    print(f"  tier 4 (wording only)  : {counts[4]}")
    assert sum(counts.values()) == len(rows), "tiers do not partition the queue"
    print(f"  {'':<25}   sum {sum(counts.values())}  (each claim in exactly one tier)")
    print(f"\n  carrying at least one flag: {out['n_with_any_flag']} of {len(rows)}")
    for f, n in out["flag_counts"].items():
        print(f"    {n:>4}  {f}")
    print("\n  Flags are advisory. They approve nothing and reject nothing.")
    print(f"  wrote {R.rel(OUT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
