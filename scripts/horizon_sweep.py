"""The horizon sweep — every horizon-indexed figure in the prose must name its horizon.

WHY THIS EXISTS. The paper was re-anchored from h=368 (the upstream's open-loop
diagnostic length) to h=100 (the method's own imagination rollout length, X-13).
The tables followed. Parts of the prose did not, and the failure is invisible to
every other check in this build: each sentence quotes a placeholder, each
placeholder resolves to a real artifact cell, and the sentence is still wrong
because the cell is at the wrong horizon. `build_paper.py` guarantees provenance;
it cannot see that a provenanced number is the other horizon's.

WHAT IT ASSERTS, over PAPER.template.md:

  1. A calibration figure — an overconfidence ratio or a coverage — must have its
     horizon named in the SENTENCE that quotes it. These are the numbers the
     paper's claims rest on and the ones a reader lifts out of context, so
     sentence scope is the right scope. Silence fails.
  2. Every other horizon-indexed value — permutation P-values, correlations,
     error floors — must have its horizon named in the enclosing PARAGRAPH.
     A reader scopes those by paragraph and the paper already writes them that
     way ("All figures in this paragraph are the held-out arena").
  3. In both cases the horizon named must be the horizon the placeholder
     resolves to. Two horizons may legitimately appear in one sentence (h=1 at
     one step against h=100 at the rollout length), so the rule is set
     containment, not equality.

TABLES. A row of a table whose first column is the horizon carries its horizon in
that cell, and is exempt. Every other table — Appendix F's claim-by-claim verdicts
above all, whose cells hold whole paragraphs of prose — is scanned like prose.
That exemption used to be "skip all table rows", and Appendix F's "Not supported
as a scale: 34.4x overconfident" is exactly what it hid.

Run standalone for the sweep report; `check_comparative_claims.py` registers it as
the `horizon-consistency` kind and fails the build on any finding.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

TEMPLATE = "PAPER.template.md"

# Placeholders that ARE a horizon: quoting one of these names the horizon.
HORIZON_NAMING_KEYS = ("v2_deploy_h", "v2_diag_h")

# The calibration family, which must name its horizon in its own sentence. A key
# is in it if it reports an overconfidence ratio, a coverage, or the ratio
# between the two uncertainty terms -- the three quantities section 6 claims on.
STRICT = re.compile(r"(ratio|_cov\d|cov1|cov2|over_alea)")


def _art(name):
    return json.load(open(os.path.join(R.RESULTS, name)))


def horizon_grid():
    """The horizon grid, from the artifact rather than typed, so a change to the
    grid cannot leave this scanner testing the old one."""
    return sorted(int(h) for h in _art("task_d_nind20.json")["d1_by_horizon"])


def deploy_diag():
    """The two load-bearing horizons, from V2 rather than from this file."""
    V2 = _art("v2_deployment_horizon.json")
    return (int(V2["verdict"]["deployment_horizon_is"]),
            int(V2["horizons"]["open_loop_diagnostic"]["value"]))


def key_horizon(key, grid):
    """The horizon a placeholder key carries, or None.

    Horizon-indexed families suffix `_h<N>`; the calibration tables also use
    `_cov<N>` for coverage at horizon N. A trailing number that is not on the
    grid is not a horizon suffix.
    """
    m = re.search(r"_h(\d+)$", key)
    if m and int(m.group(1)) in grid:
        return int(m.group(1))
    m = re.search(r"_cov(\d+)(_ci)?$", key)
    if m and int(m.group(1)) in grid:
        return int(m.group(1))
    return None


# ------------------------------------------------------------------ blocks
def blocks(text):
    """Yield (line_no, text, is_table_row, carried_scope).

    A paragraph is a blank-line-delimited run of prose lines, and its own text is
    its scope. A table is split into its rows, and a row's scope is what the
    table already says: the column header above each cell, plus the row's own
    label. That covers both shapes the paper uses — h down the first column
    (6.2's epistemic table) and h across the header ("coverage at +-1 sigma,
    h=100"). Scoping a table row by its prose alone flagged every row of both.
    """
    lines = text.split("\n")
    in_code = False
    buf, buf_line = [], 1
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code:
            i += 1
            continue
        s = ln.strip()
        if s.startswith("|"):
            if buf:
                yield buf_line, " ".join(buf), False, None
                buf = []
            # consume the whole table
            start = i
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append((i + 1, lines[i].strip()))
                i += 1
            if not rows:
                continue
            header = _cells(rows[0][1])
            horiz_col = bool(header) and header[0].strip().lower() in ("h", "horizon")
            for n, row in rows[1:]:
                cells = _cells(row)
                if not cells or set("".join(cells)) <= set("-: "):
                    continue                      # the |---|---| separator
                # Each cell is scoped by the header above it and by the row label.
                # Emitted cell by cell so a column header can scope its own column.
                # A horizon-indexed row labels itself with a bare number, which
                # names no horizon to a scanner looking for "h = N". Rewrite it.
                label = ""
                if horiz_col:
                    label = cells[0]
                    # A bare-number label names no horizon to a scanner looking
                    # for "h = N", so rewrite it -- but only when the cell IS a
                    # bare number. A cell holding {{v2_deploy_h}} already names
                    # its horizon, and digit-grabbing inside it yields the "2"
                    # of "v2".
                    bare = re.fullmatch(r"[*_ ]*(\d+)[*_ ]*", cells[0])
                    if bare:
                        label = f"h = {bare.group(1)}"
                for j, cell in enumerate(cells):
                    if "{{" not in cell:
                        continue
                    head = header[j] if j < len(header) else ""
                    yield n, cell, True, " ".join((cell, head, label))
            del start
            continue
        if s.startswith("#") or s.startswith("$$") or not s:
            if buf:
                yield buf_line, " ".join(buf), False, None
                buf = []
            i += 1
            continue
        if not buf:
            buf_line = i + 1
        buf.append(s)
        i += 1
    if buf:
        yield buf_line, " ".join(buf), False, None


def _cells(row):
    """Split a Markdown table row into cells.

    The separator is an UNESCAPED pipe. `mean \\|error\\| / mean sigma` is one
    cell, and splitting on every pipe shifted the whole header one place left,
    so every column header scoped the wrong column.
    """
    return [c.strip() for c in re.split(r"(?<!\\)\|", row.strip().strip("|"))]


_SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z*—§`\[(])")


def _resolve(text):
    """Substitute {{key}} with the value the build will print.

    The check is about what a READER sees, so it has to run on the resolved
    sentence. Two derived labels -- d2p_overlap_h ("h=100 and h=128") and
    d2b_idx_strongest_h ("h=128") -- name horizons that no literal in the
    template does, and scanning the raw template flagged the sentences carrying
    them. Typing "h = 128" beside them to satisfy the scanner would be exactly
    the hand-typed number this build exists to prevent.
    """
    N = _art("paper_numbers.json")
    return re.sub(r"\{\{([A-Za-z0-9_]+)\}\}",
                  lambda m: str(N[m.group(1)]["value"]) if m.group(1) in N else m.group(0),
                  text)


def named_horizons(text, deploy, diag, grid):
    """Every horizon the text names, in any of the forms the paper uses."""
    got = set()
    if "{{v2_deploy_h}}" in text:
        got.add(deploy)
    if "{{v2_diag_h}}" in text:
        got.add(diag)
    text = _resolve(text)
    for m in re.finditer(r"\bh\s*=?\s*(\d+)\b", text):
        if int(m.group(1)) in grid:
            got.add(int(m.group(1)))
    if re.search(r"\b(at one step|one[- ]step|at one forecast step|"
                 r"a single forecast step|step 1\b)", text, re.I):
        got.add(1)
    for m in re.finditer(r"\b(\d+)-step\b", text):
        if int(m.group(1)) in grid:
            got.add(int(m.group(1)))
    return got


def scan(text=None):
    """Return the list of offending sentences, worst first."""
    grid = horizon_grid()
    deploy, diag = deploy_diag()
    text = text if text is not None else open(TEMPLATE).read()
    findings = []
    for line_no, para, is_row, row_scope in blocks(text):
        para_named = named_horizons(para, deploy, diag, grid)
        if is_row and row_scope:
            para_named = para_named | named_horizons(row_scope, deploy, diag, grid)
        for sent in _SENT.split(para):
            sent = sent.strip()
            if not sent:
                continue
            carried = {}
            for k in re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", sent):
                h = key_horizon(k, grid)
                if h is not None:
                    carried.setdefault(h, []).append(k)
            if not carried:
                continue
            sent_named = named_horizons(sent, deploy, diag, grid)
            if is_row and row_scope:
                sent_named = sent_named | named_horizons(row_scope, deploy, diag, grid)
            for h, keys in sorted(carried.items()):
                strict = any(STRICT.search(k) for k in keys)
                scope = sent_named if strict else para_named
                if h in scope:
                    continue
                findings.append({
                    "line": line_no,
                    "scope": "sentence" if strict else "paragraph",
                    "kind": "unnamed" if not scope else "mismatch",
                    "horizon": h,
                    "keys": keys,
                    "named": sorted(scope),
                    "sentence": sent[:400],
                })
    findings.sort(key=lambda f: (f["scope"] != "sentence", f["line"]))
    return findings


def main():
    # `--file <path>` scans a template other than the working one, which is how
    # the baseline in R-70 is re-derivable: run it against the committed 24 Aug
    # template (`git show <rev>:PAPER.template.md`) and the count comes back.
    src = None
    if "--file" in sys.argv:
        src = open(sys.argv[sys.argv.index("--file") + 1]).read()
    findings = scan(src)
    grid = horizon_grid()
    d, g = deploy_diag()
    print("HORIZON SWEEP — PAPER.template.md")
    print("=" * 104)
    print(f"  horizon grid           : {grid}")
    print(f"  deployment / diagnostic: h={d} / h={g}")
    print()
    for f in findings:
        print(f"  L{f['line']:<5} {f['kind']:<8} {f['scope']:<9} carries h={f['horizon']} "
              f"{f['keys']}  names {f['named'] or '-'}")
        print(f"         {f['sentence'][:200]}")
        print()
    print("=" * 104)
    n_s = sum(1 for f in findings if f["scope"] == "sentence")
    print(f"  {len(findings)} findings — {n_s} calibration figures unscoped at sentence level, "
          f"{len(findings) - n_s} other values unscoped at paragraph level")
    out = os.path.join(R.RESULTS, "horizon_sweep.json")
    json.dump({"n_flagged": len(findings), "n_strict": n_s, "grid": grid,
               "deployment_horizon": d, "diagnostic_horizon": g,
               "findings": findings}, open(out, "w"), indent=2)
    print(f"  wrote {out}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
