"""
C1 -- the `restatement` index: every numeral in the paper, and where it came from.

THE DEFECT CLASS. All four defects an independent reader found by hand share one
shape: **a sentence restating a quantity that another section owns**, left stale
by a revision that correctly updated the owning section. Two revisions produced
three of the four -- adding h = 100 to the evaluation grid, and moving §5 from one
seed to three.

Twenty-two check kinds did not catch any of them, and could not have. Every kind
verifies a sentence against the artifact **in the section that computes it**. None
looks across sections. §5's table printed 1.66x from the three-seed artifact while
a paragraph below it printed 1.56x from the single-seed one; both numerals were
substituted, both from named artifacts, both correct about the artifact they named.
Nothing compared them, because nothing knew they were about the same quantity.

WHAT THIS INDEXES. Two populations, because the four defects came from both:

  substituted  every `{{key}}` occurrence, with its rendered value and the
               section it sits in. §5's 1.56 was of this kind.
  typed        every numeral typed into the prose that is NOT an address, a
               horizon label or a declared configuration constant -- the residue
               scripts/typed_numeral_audit.py classifies. Appendix D's "h=128"
               was of this kind: a typed restatement of a quantity §6.8 computes.

TWO ASSERTIONS.

  restatement       a rendered value appearing at more than one location must
                    resolve to the SAME key at all of them, or be registered
                    below as a coincidence with a stated reason.
  ambiguous-numeral two DIFFERENT quantities rendering to the same numeral inside
                    one section, which a reader reads as a typo or a hidden link.
                    The abstract carried 4.61x (an A/B ratio) beside 4.61%
                    (a coverage) and both were correct.

THE REGISTRY IS THE POINT. Numerals collide by chance constantly -- ratios,
counts, percentages. A check that flagged every collision would be turned off
within a day. So COINCIDENCES records each one with the reason it is not a
restatement, and the list is printed on every run. A coincidence that stops being
a coincidence has to be deleted from it by hand, which is the intended cost.

    python scripts/restatement_index.py
    python scripts/restatement_index.py --against <file>   scan another draft

Writes results/restatement_index.json.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402
import typed_numeral_audit as TNA  # noqa: E402

TEMPLATE = "PAPER.template.md"
OUT = "restatement_index.json"

# A rendered value that legitimately appears at more than one location from
# different keys. Each entry is (value, reason). The reason must say why the two
# quantities are different, not that they happen to differ.
COINCIDENCES = {
    "1.66": "the hold-last floor ratio at h=368 and the sigma-growth factor at h=1 "
            "in §6.10's decomposition table; unrelated quantities, and the pair that "
            "made §5's stale 1.56 look plausible for a revision",
    "2.8": "Arm A's margin over the floor at h=368, and the trunk-sharing improvement "
           "in §6.10; both are ratios of unrelated things",
    "45": "the state dimensionality, which is the denominator of every per-dimension "
          "count and is one quantity appearing many times",
    "1.0": "the value a ratio takes when two quantities are equal",
    "2.0": "Arm A's margin over the floor at h=100, and the ensemble-topology "
           "member count; unrelated",
    "4": "the independent-trajectory count of the out-of-sample arena and several "
         "small counts; §3 fixes the first and §12 bounds every claim by it",
    "100": "the deployment horizon, a percentage, and a share; the horizon is "
           "substituted from v2_deploy_h everywhere it is a horizon",
    "68.27": "the calibrated coverage at +-1 sigma, one constant used in many places",
}

# (section, value) pairs adjudicated as not an ambiguity, with the reason.
ACCEPTED_AMBIGUOUS = {
    ("6.10 Testing the mechanism: an ensemble that shares nothing", "3"):
        "the shared-trunk seed count in prose against a percentage share in a "
        "cell of the decomposition table. Different units, different places, and "
        "no sentence puts them side by side -- unlike the abstract's 4.61x beside "
        "4.61%, which is what this kind exists for",
}


# Classes whose members cannot possibly restate a measurement. Everything else --
# horizon labels, iteration counts, dimensionalities -- stays in the population,
# because a typed one of those beside a derived one is precisely the defect.
ADDRESS_CLASSES = {"section-ref", "subsection-heading", "markdown-heading",
                   "arxiv-id", "version-tag", "ledger-id", "figure-ref",
                   "equation-ref", "table-ref", "orig-section", "code-location",
                   "citation-year", "date", "table-row-label"}


def _sigdigits(v):
    """Significant digits, as a crude measure of how surprising a collision is.

    "0", "4" and "100" collide constantly and mean nothing. "0.4187" colliding
    across two keys is either the same quantity twice or a coincidence worth
    someone looking at.
    """
    return len(re.sub(r"[-+.,]|^0+|0+$", "", v)) or len(re.sub(r"[-+.,]", "", v))


def sections(text):
    """(start, title) for every heading, so a location can be named."""
    out = []
    for m in re.finditer(r"^(#{2,3}) +(.+)$", text, re.M):
        out.append((m.start(), m.group(2).strip()))
    return out


def _section_of(secs, pos):
    name = "front matter"
    for start, title in secs:
        if start <= pos:
            name = title
        else:
            break
    return name


def scan(text, values):
    """Both populations, as [{value, key|None, section, line, ctx}].

    Substituted occurrences are located in the TEMPLATE; typed ones in the
    PREPARED text, which is shorter. Two section tables, because one offset
    scheme cannot serve both.
    """
    secs = sections(text)
    prepared = TNA.prepare(text)
    psecs = sections(prepared)
    rows = []
    # ---- substituted
    for m in re.finditer(r"\{\{([A-Za-z0-9_]+)\}\}", text):
        k = m.group(1)
        if k not in values:
            continue
        v = str(values[k]["value"]).strip()
        if not re.fullmatch(r"[-+]?\d[\d,]*\.?\d*", v):
            continue          # lists, words, id strings: not numerals
        # what the value is a quantity OF, taken from the character(s) that follow
        after = text[m.end():m.end() + 3]
        unit = ("%" if after.startswith("%") else
                "x" if after.startswith("\u00d7") else
                "pts" if after.startswith(" points") else "")
        rows.append({"value": v, "key": k, "unit": unit,
                     "section": _section_of(secs, m.start()),
                     "line": text[:m.start()].count("\n") + 1,
                     "ctx": re.sub(r"\s+", " ", text[max(0, m.start() - 70):m.end() + 40])})
    # ---- typed, minus the ADDRESSES only
    #
    # Not minus the declared constants, and this distinction is the whole check.
    # typed_numeral_audit.py exists to say "this typed numeral is not a
    # measurement", and it classifies `h=128` as a horizon label -- correctly, for
    # its purpose. But `h=128` in appendix D was a typed RESTATEMENT of the
    # extremum §6.8 derives, and it was wrong. Filtering the population by that
    # audit would drop exactly the numeral this check exists to find.
    #
    # So only the classes that are addresses in the strict sense are removed: a
    # section number, an arXiv id, a file:line, a citation year. Nothing there can
    # restate a measured quantity.
    for sp in TNA._spans(text, prepared):
        c = TNA.classify(sp)
        if c is not None and c.split(":")[0] in ADDRESS_CLASSES:
            continue
        rows.append({"value": sp["num"], "key": None, "typed_class": c,
                     # sp["pos"] is the offset in the SCANNED text, which is the
                     # template with placeholders replaced by a one-char sentinel
                     # and code fences dropped. text.find(linetext) was used here
                     # and returned the FIRST line matching, so every repeated
                     # line -- every table row -- was attributed to whichever
                     # section held its first copy, and dozens landed in "front
                     # matter".
                     "section": _section_of(psecs, sp["pos"]),
                     "line": sp["line"], "ctx": re.sub(r"\s+", " ", sp["ctx"])})
    return rows


# (typed numeral, key) pairs adjudicated as not a restatement. Each needs a
# reason in the comment beside it; the list is printed on every run.
ACCEPTED_TYPED = {
}

# Keys that NAME the evaluation grid rather than report a result. Every "h = 8"
# in the paper shares a slot with these by construction, so leaving them as match
# targets made every horizon label in the document a candidate restatement -- 21
# of them, all false. A horizon label is only a restatement when it restates a
# horizon some other sentence DERIVES, like §6.8's worst-calibrated cell.
GRID_KEYS = {"v2_deploy_h", "v2_diag_h", "v2_len_eval", "v2_history"}

STOP = {"which", "where", "there", "these", "those", "their", "other", "about",
        "than", "that", "this", "with", "from", "into", "over", "under", "every",
        "paper", "section", "because", "rather", "would", "could", "should",
        "against", "between", "before", "after", "while", "whole", "still",
        "first", "second", "third", "here", "were", "been", "have", "does"}


def _content(sentence):
    """Distinctive words of a sentence: >=6 letters, not structural."""
    return {w for w in re.findall(r"[a-z]{6,}", sentence.lower()) if w not in STOP}


def _sentence_at(text, pos):
    a = max(text.rfind(". ", 0, pos), text.rfind("\n\n", 0, pos),
            text.rfind("; ", 0, pos), text.rfind("| ", 0, pos))
    b = min([x for x in (text.find(". ", pos), text.find("\n\n", pos),
                         text.find("; ", pos), text.find(" |", pos)) if x > 0]
            or [len(text)])
    return text[a + 1:b]


def typed_restatements(text, values, min_shared=2):
    """A typed numeral standing in the slot that a placeholder fills elsewhere.

    THE MECHANISM, and why a value-collision index is not enough. Appendix D
    typed "the largest deviation is aleatoric at h=128" while §6.8 wrote "The
    largest deviation over all N held-out cells is {{d3_worst_q}} at
    h={{d3_worst_h}}". After h = 100 entered the evaluation grid §6.8 re-derived
    and printed 100; the appendix sentence, which describes the CORRECTION of an
    earlier defect, still said 128. Nothing collided, because 128 no longer
    appeared anywhere as a substituted value -- the stale copy was the only place
    it survived. A value-collision index cannot see that by construction.

    So this matches on the SLOT instead. Two signals must both hold:

      1. the typed numeral and the placeholder are preceded by the same token
         ("h=", "at ", "of "), so they occupy the same position in a sentence;
      2. their sentences share at least `min_shared` distinctive words, so they
         are talking about the same thing rather than sharing a preposition.

    A disagreement between the two is a stale restatement. Agreement is a typed
    copy of a derived value, which is the same defect one revision earlier.
    """
    out = []
    keyed = []
    prepared = TNA.prepare(text)
    # Walk the template for the keys, but take each one's sentence from the
    # PREPARED text at the matching sentinel, so both sides of the comparison are
    # in one coordinate system.
    sentinels = [m.start() for m in re.finditer("\u2400", prepared)]
    ph = [m for m in re.finditer(r"\{\{([A-Za-z0-9_]+)\}\}", text)]
    if len(sentinels) != len(ph):
        sentinels = None
    for n, m in enumerate(ph):
        k = m.group(1)
        if k not in values:
            continue
        v = str(values[k]["value"]).strip()
        if not re.fullmatch(r"[-+]?\d[\d,]*\.?\d*", v):
            continue
        pos = sentinels[n] if sentinels else m.start()
        pre = prepared[max(0, pos - 6):pos] if sentinels else text[max(0, pos - 6):pos]
        keyed.append({"key": k, "value": v, "pre": pre.strip()[-4:].lower(),
                      "sent": _sentence_at(prepared if sentinels else text, pos),
                      "pos": pos})
    secs = sections(prepared if sentinels else text)
    for sp in TNA._spans(text, prepared):
        c = TNA.classify(sp)
        if c is not None and c.split(":")[0] in ADDRESS_CLASSES:
            continue
        stext = _sentence_at(prepared, sp["pos"])
        pre = sp["ctx"][max(0, sp["off"] - 6):sp["off"]].strip()[-4:].lower()
        words = _content(stext)
        # The BEST match, not the first. Taking the first meant a typed numeral
        # was compared against whichever key happened to appear earliest in the
        # document with the same slot, and appendix D's h=128 was matched to a
        # horizon label three hundred lines above the sentence it restates.
        # The numeral must be BOUND to a name -- "h=128", "n=10", "= 0.05" -- not
        # merely preceded by a word. A numeral after "and" or "the" is prose, and
        # matching on prose slots produced five more false positives whose shared
        # words were coincidental.
        if not pre.endswith("=") and not pre.endswith("= "):
            continue
        best, best_shared = None, set()
        for kd in keyed:
            if kd["pre"] != pre or not pre or kd["key"] in GRID_KEYS:
                continue
            shared = words & _content(kd["sent"])
            if len(shared) >= min_shared and len(shared) > len(best_shared):
                best, best_shared = kd, shared
        if best is None:
            continue
        if (sp["num"], best["key"]) in ACCEPTED_TYPED:
            continue
        out.append({"typed": sp["num"], "key": best["key"],
                    "key_value": best["value"],
                    "agrees": sp["num"] == best["value"],
                    "slot": pre, "shared": sorted(best_shared)[:6],
                    "typed_line": sp["line"],
                    "typed_section": _section_of(secs, sp["pos"]),
                    "key_section": _section_of(secs, best["pos"]),
                    "typed_ctx": re.sub(r"\s+", " ", stext)[:150]})
    return out


def analyse(rows, values):
    by_value = {}
    for r in rows:
        by_value.setdefault(r["value"], []).append(r)

    restatements, ambiguous = [], []
    for v, group in sorted(by_value.items()):
        keys = {r["key"] for r in group}
        if len(group) < 2 or len(keys) < 2:
            continue
        if v in COINCIDENCES:
            continue
        typed = [r for r in group if not r["key"]]
        subst = [r for r in group if r["key"]]
        srcs = {values[r["key"]]["source"] for r in subst}
        # Two tiers, because a check everyone turns off protects nothing.
        #
        #   blocking  a TYPED numeral equal to a value another section derives
        #             (appendix D's h=128 against §6.8's derived extremum), or a
        #             collision across DIFFERENT artifacts on a value distinctive
        #             enough that chance is a poor explanation (§5's 1.56 from the
        #             single-seed pair against §6.10's sigma ratio).
        #   advisory  everything else: two cells of one table, or a two-digit
        #             value that collides by arithmetic.
        # WHAT BLOCKS, and why it is not this.
        #
        # A value collision catches the LATENT form of the defect, not the live
        # one. §5's stale 1.56 was found here only because it happened to equal
        # §6.10's unrelated sigma ratio; had it not, the two floor ratios would
        # have been 1.56 and 1.66 and collided with nothing. What a collision
        # reliably finds is a pair of keys that are the same quantity and AGREE
        # today -- e5_cov1_h100 and r2_shared_cov1_h100 both printing 8.19% from
        # two artifacts -- which is precisely the state §5 was in before one of
        # its two keys moved to three seeds.
        #
        # That is a queue for a person, not a build failure: each pair is the
        # question "are these the same quantity?", and 34 of them stand today.
        # They go to the C1 review as Tier 0 (see scripts/c2_revision_cohorts.py).
        # The two kinds that DO block -- typed-restatement and ambiguous-numeral
        # -- are precise enough to be right every time, and both stand at zero.
        same_quantity_candidate = (bool(typed and subst)
                                   or (len(srcs) > 1 and _sigdigits(v) >= 3))
        restatements.append({
            "value": v, "n_locations": len(group),
            # NOT "blocking". It was called that and nothing blocked on it: the
            # artifact read n_blocking 37 while main() returned 0. A field named
            # for an effect it does not have is worse than no field, because a
            # reader of the artifact -- or of a commit message quoting it --
            # concludes the build is enforcing something it is not. These are
            # candidates for a person to adjudicate, and the two kinds that DO
            # fail the build are typed-restatement and ambiguous-numeral.
            "same_quantity_candidate": same_quantity_candidate,
            "fails_build": False,
            "n_typed": len(typed), "n_substituted": len(subst),
            "sources": sorted(srcs),
            "keys": sorted(str(k) for k in keys),
            "locations": [{"section": r["section"], "line": r["line"],
                           "key": r["key"], "ctx": r["ctx"][-110:]} for r in group]})

    by_sec = {}
    for r in rows:
        by_sec.setdefault((r["section"], r["value"]), []).append(r)
    for (sec, v), group in sorted(by_sec.items()):
        keys = {r["key"] for r in group if r["key"]}
        if len(keys) < 2 or v in COINCIDENCES:
            continue
        # Two keys rendering the same value in one section is ordinary and mostly
        # deliberate: "5 of 5", "10 of 10", a count beside its total. What misleads
        # is the same NUMERAL carrying different UNITS -- the abstract printed
        # 4.61x (an A/B ratio) beside 4.61% (a coverage), and a reader assumes a
        # typo or a hidden link between them. Unit-blind, this kind fired 53 times
        # on the same draft and would have been ignored.
        # Units PER KEY, not pooled. Pooled, one key written "**2.03×**" in a
        # table and "a factor of 2.03" in prose looked like two quantities
        # wearing two units, and the kind fired on a key colliding with itself.
        per_key = {}
        for r in group:
            if r["key"]:
                per_key.setdefault(r["key"], set()).add(r.get("unit", ""))
        dominant = {k: sorted(u)[-1] for k, u in per_key.items()}
        if len(set(dominant.values())) < 2:
            continue
        units = sorted(set(dominant.values()))
        if (sec, v) in ACCEPTED_AMBIGUOUS:
            continue
        ambiguous.append({"section": sec, "value": v, "keys": sorted(keys),
                          "units": sorted(units),
                          "lines": [r["line"] for r in group]})
    return restatements, ambiguous


# The drafts each defect actually stood in, and what must fire against them.
# A check validated only against the tree it was written from is the vacuous
# assertion this project has now recorded four times, so --acceptance re-runs
# both from git and asserts on the result.
#
# The revision brief asked for both to fire against the 24 August draft. B2 does.
# B1 does not exist there and cannot: the 24 August draft has no three-seed A/B
# table, so §5's single-seed floor ratio was the only one and was correct for the
# artifact it named. The contradiction was created by the revision that added the
# table (39ac8a1) and stood at adc6d88, which is where B1 is tested.
ACCEPTANCE = [
    {"commit": "dd63abf", "label": "24 August draft", "defect": "B2",
     "kind": "typed-restatement",
     "expect": "appendix D types h=128 where §6.8 derives d3_worst_h=100"},
    {"commit": "adc6d88", "label": "the revision-2 head", "defect": "B1",
     "kind": "restatement",
     "expect": "§5's B_over_floor=1.56 collides with §6.10's r2_sigma_x_h1"},
    {"commit": "adc6d88", "label": "the revision-2 head", "defect": "B9",
     "kind": "ambiguous-numeral",
     "expect": "the abstract prints 4.61 as both x and %"},
]


def acceptance():
    """Re-run the check against the drafts the defects stood in."""
    import subprocess
    import tempfile
    ok = True
    print("C1 — ACCEPTANCE: the check must fire on the defects it was written for")
    print("=" * 96)
    for a in ACCEPTANCE:
        with tempfile.TemporaryDirectory() as d:
            for f, dest in (("PAPER.template.md", "tpl"),
                            ("results/paper_numbers.json", "pn")):
                blob = subprocess.run(["git", "show", f'{a["commit"]}:{f}'],
                                      capture_output=True, text=True)
                if blob.returncode:
                    print(f"  SKIP  {a['defect']}: cannot read {f} at {a['commit']}")
                    ok = False
                    break
                open(os.path.join(d, dest), "w").write(blob.stdout)
            else:
                text = open(os.path.join(d, "tpl")).read()
                vals = json.load(open(os.path.join(d, "pn")))
                rows = scan(text, vals)
                res, amb = analyse(rows, vals)
                tr = typed_restatements(text, vals)
                if a["kind"] == "typed-restatement":
                    fired = [x for x in tr if x["typed"] == "128"
                             and x["key"] == "d3_worst_h"]
                elif a["kind"] == "ambiguous-numeral":
                    fired = [x for x in amb if x["value"] == "4.61"]
                else:
                    fired = [x for x in res if x["value"] == "1.56"
                             and "B_over_floor" in x["keys"]]
                print(f"  {'FIRES' if fired else 'MISSED':<7} {a['defect']:<4} "
                      f"{a['kind']:<18} {a['label']:<20} ({a['commit']})")
                print(f"          {a['expect']}")
                ok = ok and bool(fired)
    # ...and must NOT fire on the fixed tree, or the fix is not a fix
    text = open(TEMPLATE).read()
    vals = json.load(open(os.path.join(R.RESULTS, "paper_numbers.json")))
    tr = typed_restatements(text, vals)
    _, amb = analyse(scan(text, vals), vals)
    clean = not tr and not amb
    print(f"  {'CLEAN' if clean else 'STILL FIRING':<7} —    current tree: "
          f"{len(tr)} typed restatements, {len(amb)} ambiguous numerals")
    print("=" * 96)
    print("  " + ("acceptance passed" if ok and clean else "ACCEPTANCE FAILED"))
    return 0 if (ok and clean) else 1


def main():
    if "--acceptance" in sys.argv:
        return acceptance()
    # The acceptance run is a PRECONDITION of reporting, not a flag.
    #
    # reproduce.sh invoked this script without --acceptance, so on every build the
    # index ran and the proof that it can fire on a real defect ran never. The
    # typed-numeral audit had the same shape and its self-test had been broken for
    # several commits before anything noticed. A check whose validation only runs
    # when asked is a check whose validation stops running.
    #
    # Skipped only where git history is unavailable, and then loudly: the
    # acceptance replays two historical commits, and a shallow clone has neither.
    if "--no-acceptance" not in sys.argv:
        import subprocess as _sp
        _has_git = _sp.run(["git", "rev-parse", "--verify", "-q",
                            ACCEPTANCE[0]["commit"] + "^{commit}"],
                           capture_output=True).returncode == 0
        if not _has_git:
            print("  WARNING: acceptance skipped — commit "
                  f"{ACCEPTANCE[0]['commit']} is not in this clone's history, so "
                  "the check cannot be shown to fire on the defects it was written "
                  "for. The index below is reported without that proof.")
        elif acceptance() != 0:
            print("\n  ACCEPTANCE FAILED — the index is not reported. A restatement "
                  "check that no longer fires on B1, B2 or B9 is not a check.")
            return 1
        print()
    path = TEMPLATE
    if "--against" in sys.argv:
        path = sys.argv[sys.argv.index("--against") + 1]
    text = open(path).read()
    values = json.load(open(os.path.join(R.RESULTS, "paper_numbers.json")))
    rows = scan(text, values)
    restatements, ambiguous = analyse(rows, values)
    typed_rs = typed_restatements(text, values)

    print("C1 — RESTATEMENT INDEX")
    print("=" * 96)
    print(f"  scanned            : {path}")
    print(f"  substituted numerals: {sum(1 for r in rows if r['key'])}")
    print(f"  typed numerals kept : {sum(1 for r in rows if not r['key'])}"
          f"  (addresses and declared constants excluded)")
    print(f"  registered coincidences: {len(COINCIDENCES)}")
    print()
    blocking = [x for x in restatements if x["same_quantity_candidate"]]
    advisory = [x for x in restatements if not x["same_quantity_candidate"]]
    if restatements:
        print(f"  {len(restatements)} value(s) appear at more than one location from more "
              f"than one key:")
        print(f"    {len(blocking)} same-quantity candidates — a distinctive value "
              f"shared across artifacts, or a typed copy of a derived one")
        print(f"    {len(advisory)} lower-signal — a short value, or two cells of one table")
        print(f"    none of these fails the build; they are the C1 review's Tier 0 queue")
        print()
        for x in blocking:
            print(f"    {x['value']:>10}  keys {x['keys']}")
            for loc in x["locations"]:
                print(f"                §{loc['section'][:34]:<34} L{loc['line']:<5} "
                      f"{loc['key'] or 'TYPED':<26} ...{loc['ctx'][-70:]}")
    else:
        print("  no restatements: every repeated value resolves to one key, or is registered")
    if typed_rs:
        print(f"\n  {len(typed_rs)} TYPED RESTATEMENT(S) — a literal in the slot a "
              f"placeholder fills elsewhere:")
        for x in typed_rs:
            print(f"    §{x['typed_section'][:30]:<30} L{x['typed_line']:<5} "
                  f"typed {x['typed']:>8}  slot {x['slot']!r:>8}  vs "
                  f"{x['key']}={x['key_value']} (§{x['key_section'][:24]}) "
                  f"{'AGREES' if x['agrees'] else 'DISAGREES'}")
            print(f"        shared: {x['shared']}")
            print(f"        {x['typed_ctx'][:120]}")
    else:
        print("  no typed restatements: no literal sits in a slot a placeholder fills")
    if ambiguous:
        print(f"\n  {len(ambiguous)} AMBIGUOUS NUMERAL(S) — two quantities, one numeral, one section:")
        for x in ambiguous:
            print(f"    §{x['section'][:36]:<36} {x['value']:>9} as {x['units']}  "
                  f"{x['keys']}  lines {x['lines']}")
    else:
        print("  no ambiguous numerals: no section prints two quantities as the same numeral")

    rec = {"scanned": path, "n_substituted": sum(1 for r in rows if r["key"]),
           "n_typed": sum(1 for r in rows if not r["key"]),
           "n_restatements": len(restatements),
           "n_same_quantity_candidates": len(blocking),
           "n_lower_signal": len(advisory), "restatements": restatements,
           "what_fails_the_build": ["typed-restatement", "ambiguous-numeral"],
           "what_does_not": ("value collisions between two substituted keys. They "
                             "are the C1 review's Tier 0 queue, not a build "
                             "failure: each is the question 'are these two keys "
                             "the same quantity?', which needs a person."),
           "n_ambiguous": len(ambiguous), "ambiguous": ambiguous,
           "n_typed_restatements": len(typed_rs), "typed_restatements": typed_rs,
           "coincidences": COINCIDENCES}
    if path == TEMPLATE:
        json.dump(rec, open(os.path.join(R.RESULTS, OUT), "w"), indent=2)
        print(f"\n  wrote results/{OUT}")
    return 1 if (ambiguous or typed_rs) else 0


if __name__ == "__main__":
    sys.exit(main())
