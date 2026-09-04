"""A -- sweep every pointer in the paper against what it now points at.

WHY, and why it is not a new check kind. Three defects of one class appeared in two
sessions:

  - `retraction-consistency` lost a surface when Appendix D's machinery moved (5a);
  - `count-consistency` lost the same surface, in a different check (5b);
  - §8's closing sentence still pointed at Appendix D for "the argument, the kinds, the
    self-test, the defects" -- none of which Appendix D holds any more (5b).

The first two were check-coverage gaps and `scripts/check_scope_audit.py` found them. The
third is different in kind and is the one that would have shipped: the reference RESOLVED.
`part_f_gate` check 5 confirms every section cross-reference points at a section that
exists, and §8's did. What was wrong was the CLAIM ABOUT WHAT THE TARGET CONTAINS, and
nothing in the registry validates that.

So this sweeps five pointer classes:

  semantic    "§X gives ...", "Appendix Y sets out ..." -- does the target still contain
              what the sentence says it does? Checked by requiring the pointer's own nouns
              to appear in the target section.
  artifact    "results/foo.json" -- does the file exist?
  repo        "src/foo.py:123" -- does the file exist and have that line?
  upstream    "system_dynamics.py:126" -- does the pinned upstream file have that line?
  new docs    docs/BUILD_CHECKS.md, docs/APPENDIX_G_RULES.md -- do they exist?

ONE PASS, not a registered kind. Session 5 removed machinery, and this is a one-time
consequence of moving text rather than a recurring risk once the moves are done. It is
recorded so a reader can see it ran.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

PAPER = "PAPER.md"
# BOTH pinned upstreams. The first sweep searched only robotic_world_model_lite and
# reported thirteen system_dynamics.py citations as UNVERIFIED; that file lives in
# rsl_rl_rwm. A sweep that reports a citation unverifiable because it looked in one of
# two places is worse than not sweeping, because it launders a bug as a caveat.
UPSTREAMS = [os.path.join("..", "robotic_world_model_lite"),
             os.path.join("..", "rsl_rl_rwm")]

# Words that carry no information about what a target holds.
STOP = set("the a an of and or to in for on at is are was were that which this those it its "
           "as by with from what how why we our their than then so not no all every each one "
           "two three four five six own into onto over under after before both same other".split())


# Flags resolved by reading the sentence. A flag NOT listed here stays unresolved and is
# reported as such -- the table records review, it does not suppress.
#
# Both entries below are the same false positive: the heuristic assumes the object of
# "gives"/"explains" FOLLOWS the pointer, and in an appositive it precedes it. "the one
# §6.3 explains -- is computed on every imagination step and discarded" reads to the
# matcher as a claim that §6.3 explains the discarding. The pointer is correct.
REVIEWED = {
    "§6.3 explains — is computed on every imagination step and discarded": (
        "CORRECT — appositive. The sentence is 'the aleatoric head ... the one §6.3 "
        "explains'; §6.3 is titled 'Why the aleatoric head collapses'. The text the "
        "matcher scored is the clause after the em-dash, not the claim."),
    "§2 gives the prior work and the": (
        "CORRECT — §2 contains Malik, Kuleshov, 'calibrated' and 'well ranked', verified "
        "directly. The absent tokens are 'prior' and the hyphenated compound this "
        "sentence coins, neither of which the target needs to contain."),
}


def sections(md):
    """Map '6.2' / 'Appendix D' -> that section's text, from the built paper."""
    out, cur, buf = {}, None, []
    for line in md.split("\n"):
        m = re.match(r"^#{2,3} (?:(\d+(?:\.\d+)?)\.?|Appendix ([A-Z]))\s*[—-]?\s*(.*)$", line)
        if m:
            if cur:
                out[cur] = "\n".join(buf)
            cur = m.group(1) or f"Appendix {m.group(2)}"
            buf = [line]
        elif cur:
            buf.append(line)
    if cur:
        out[cur] = "\n".join(buf)
    return out


def upstream_ok(fn, line):
    """The pinned upstream is fetched by setup.sh and is not in this repo. If it is
    absent the citation is UNVERIFIED -- which is itself the finding, per the brief's
    standing rule 1 -- rather than silently passing."""
    for up in UPSTREAMS:
        for root, _, names in os.walk(up):
            if fn in names:
                p = os.path.join(root, fn)
                n = len(open(p, encoding="utf-8", errors="replace").read().split("\n"))
                return n >= line, p
    return None, None


def main():
    md = open(PAPER).read()
    secs = sections(md)
    rows, bad = [], []

    def rec(kind, ptr, ok, detail, ctx=""):
        r = {"class": kind, "pointer": ptr, "ok": ok, "detail": detail}
        if ctx:
            r["context"] = ctx[:180]
        if ok is False:
            for key, why in REVIEWED.items():
                if ptr.startswith(key) or key in ptr:
                    r["reviewed"] = why
                    r["ok"] = "reviewed-correct"
                    break
        rows.append(r)
        if r["ok"] is False:
            bad.append(r)

    # ---- 1. semantic pointers: does the target hold what the sentence claims? ----
    verb = r"(?:gives|sets out|records|lists|holds|explains|spends|says|quotes|carries|enumerates)"
    for m in re.finditer(r"(§(\d+(?:\.\d+)?)|Appendix ([A-Z]))\s+(" + verb + r")\s+([^.;]{0,150})", md):
        tgt = m.group(2) or f"Appendix {m.group(3)}"
        claim = m.group(5)
        body = secs.get(tgt)
        if body is None:
            rec("semantic", f"{m.group(1)} {m.group(4)}", False, f"target {tgt} not found")
            continue
        nouns = [w for w in re.findall(r"[a-z][a-z-]{3,}", claim.lower()) if w not in STOP]
        low = body.lower()
        missing = [w for w in nouns if w not in low and w.rstrip("s") not in low]
        # A pointer is suspect when MOST of what it promises is absent from the target.
        ok = not nouns or len(missing) <= max(1, len(nouns) // 2)
        rec("semantic", f"{m.group(1)} {m.group(4)} {claim[:60]}", ok,
            f"target {tgt}; nouns {nouns}; absent {missing}", m.group(0))

    # ---- 2. artifact paths ----
    for p in sorted(set(re.findall(r"results/[\w./-]+\.json", md))):
        rec("artifact", p, os.path.exists(p), "exists" if os.path.exists(p) else "MISSING")

    # ---- 3. repo file:line ----
    for c in sorted(set(re.findall(r"(?:src|scripts)/[\w./-]+\.py:\d+(?:-\d+)?", md))):
        f, _, ln = c.partition(":")
        first = int(ln.split("-")[0])
        ok = os.path.exists(f) and len(open(f).read().split("\n")) >= first
        rec("repo", c, ok, "resolves" if ok else "file missing or too short")

    # ---- 4. upstream file:line ----
    for c in sorted(set(re.findall(
            r"(?:[\w/]*/)?((?:system_dynamics|model_training|base|anymal_d_flat)\.py):(\d+)", md))):
        fn, ln = c
        ok, path = upstream_ok(fn, int(ln))
        rec("upstream", f"{fn}:{ln}",
            ok if ok is not None else None,
            f"{path} has the line" if ok else
            ("UNVERIFIED — pinned upstream not present in this tree (setup.sh fetches it)"
             if ok is None else f"{path} is shorter than {ln}"))

    # ---- 5. the surfaces 5a and 5b created ----
    for p in sorted(set(re.findall(r"docs/(?:BUILD_CHECKS|APPENDIX_G_RULES)\.md", md))):
        rec("new-docs", p, os.path.exists(p), "exists" if os.path.exists(p) else "MISSING")

    out = {
        "sweep": "every pointer in the paper against what it now points at",
        "why": ("part_f_gate check 5 confirms a section cross-reference RESOLVES. §8's "
                "pointer resolved and was still wrong, because what it claimed the target "
                "contains had moved. This sweeps the claim, not the link."),
        "not_a_check_kind": ("deliberate. Session 5 removed machinery, and this is a "
                             "one-time consequence of moving text rather than a recurring "
                             "risk once the moves are done."),
        "classes": ["semantic", "artifact", "repo", "upstream", "new-docs"],
        "n_pointers": len(rows),
        "n_ok": sum(1 for r in rows if r["ok"] is True),
        "n_reviewed_correct": sum(1 for r in rows if r["ok"] == "reviewed-correct"),
        "reviewed": [r for r in rows if r["ok"] == "reviewed-correct"],
        "n_unverified": sum(1 for r in rows if r["ok"] is None),
        "n_bad": len(bad),
        "bad": bad,
        "pointers": rows,
    }
    op = os.path.join(R.RESULTS, "xref_sweep.json")
    json.dump(out, open(op, "w"), indent=2)

    print("=" * 96)
    print("CROSS-REFERENCE SWEEP — what each pointer claims its target holds")
    print("=" * 96)
    for k in out["classes"]:
        sub = [r for r in rows if r["class"] == k]
        print(f"  {k:10} {len(sub):>3} pointers, "
              f"{sum(1 for r in sub if r['ok'] is True):>3} ok, "
              f"{sum(1 for r in sub if r['ok'] == 'reviewed-correct'):>2} reviewed, "
              f"{sum(1 for r in sub if r['ok'] is None):>2} unverified, "
              f"{sum(1 for r in sub if r['ok'] is False):>2} suspect")
    if bad:
        print(f"\n  SUSPECT ({len(bad)}):")
        for r in bad:
            print(f"    !! [{r['class']}] {r['pointer'][:88]}")
            print(f"       {r['detail'][:140]}")
    print(f"\n  wrote {R.rel(op)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
