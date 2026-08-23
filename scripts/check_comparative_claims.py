"""Part C — verify the paper's COMPARATIVE claims, not just its numerals.

The numeral check (build_paper.py) guarantees every printed number came from an
artifact. It cannot see a sentence that takes correct numbers and asserts a wrong
relation between them. Six such defects shipped in this paper before anyone
looked: an arena switched silently mid-claim, an overlap that was not one, a sign
reversed, an extremum that was third-largest, and two orders-of-magnitude
descriptions that disagreed with each other about the same ratio.

Each entry below pins TWO things:

  says    a fragment that must appear in the built PAPER.md. If the prose is
          reworded the check fails loudly rather than silently drifting off the
          sentence it was written to guard.
  expect  a relation recomputed from the artifacts.

Both must hold. A check that only re-asserts an artifact fact guards nothing; a
check that only matches text guards nothing either.

Kinds, matching the five failures they were written for:

  overlap    two intervals overlap, or do not                        (A2)
  extremum   the named cell is the max/min of its family             (A4)
  sign       a stated rise/fall matches the sign of b - a            (A3)
  orders     "N orders of magnitude" matches round(log10(ratio))     (A5)
  cell       a k/n count in the text is the cell the text names,
             with its arena and horizon                              (A1)

Run with --self-test to corrupt each check in turn and confirm it fails. An
assertion that has never failed has not been tested.

Writes results/comparative_claims.json.
"""
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

PAPER = "PAPER.md"
_cache = {}
WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven",
         8: "Eight", 9: "Nine", 10: "Ten"}


def _window(text, frag, span=160):
    """The text around a fragment, where the count that qualifies it must appear."""
    i = text.find(frag)
    return "" if i < 0 else text[max(0, i - span):i + len(frag) + span]


def art(name):
    if name not in _cache:
        _cache[name] = json.load(open(os.path.join(R.RESULTS, name)))
    return _cache[name]


def dig(name, path):
    """dig('task_d_nind20.json', 'd2_forecast_index.128.ci.index.lo')"""
    o = art(name)
    for k in path.split("."):
        o = o[int(k)] if isinstance(o, list) else o[k]
    return o


# ---------------------------------------------------------------- the claims
CLAIMS = [
    # ---- C1 overlap (A2) -------------------------------------------------
    {"id": "C1.1", "kind": "overlap", "where": "5.6",
     "says": "the marginal intervals *do* overlap",
     "a": ("task_d_nind20.json", "d2_forecast_index.128.ci.index"),
     "b": ("task_d_nind20.json", "d2_forecast_index.128.ci.epistemic"),
     "expect": "overlap"},
    {"id": "C1.2", "kind": "overlap", "where": "5.6",
     "says": "excludes zero at",
     "a": ("task_d_nind20.json", "d2_forecast_index.368.ci.index"),
     "b": ("task_d_nind20.json", "d2_forecast_index.368.ci.epistemic"),
     "expect": "disjoint"},
    # ---- C2 extremum (A4) ------------------------------------------------
    {"id": "C2.1", "kind": "extremum", "where": "5.7",
     "says": "The largest deviation over all",
     "family": ("task_d3_perhorizon.json", "d3_cells"),
     "named": {"quantity": "aleatoric", "h": 128, "fit_episode": 8},
     "expect": "max"},
    {"id": "C2.2", "kind": "extremum", "where": "5.6",
     "says": "is the smallest lower bound in the table",
     "family": ("task_d_nind20.json", "d2_paired_lo"),
     "named": {"h": "128"},
     "expect": "min"},
    # ---- C3 sign (A3) ----------------------------------------------------
    {"id": "C3.1", "kind": "sign", "where": "5.6",
     "says": "*lowers* disagreement's correlation by",
     "a": ("task_d2b_robustness.json", "raw.r_disagreement_error"),
     "b": ("task_d2b_robustness.json", "controls.linear.r_disagreement_given_index"),
     "expect": "fall"},
    {"id": "C3.2", "kind": "sign", "where": "abstract",
     "says": "lowers disagreement's correlation by only",
     "a": ("task_d2b_robustness.json", "raw.r_disagreement_error"),
     "b": ("task_d2b_robustness.json", "controls.linear.r_disagreement_given_index"),
     "expect": "fall"},
    {"id": "C3.3", "kind": "sign", "where": "5.6",
     "says": "removing the shared depth trend",
     "a": ("task_d2b_robustness.json", "raw.r_disagreement_error"),
     "b": ("task_d2b_robustness.json", "controls.within_step.r_disagreement_given_index"),
     "expect": "rise", "optional": True},
    # ---- C4 orders of magnitude (A5) -------------------------------------
    {"id": "C4.1", "kind": "orders", "where": "5.2 / abstract / 12",
     "says": "× better than aleatoric at the deployment horizon",
     "num": ("task_d_nind20.json", "d1_by_horizon.368.aleatoric.ratio_err_over_sigma"),
     "den": ("task_d_nind20.json", "d1_by_horizon.368.epistemic.ratio_err_over_sigma"),
     "stated_orders": None},
    {"id": "C4.2", "kind": "orders", "where": "5.5",
     "says": "a factor of about 10^",
     "num": ("task_b_permutation.json",
             "arenas.in-sample.models.teacher-forced armB.368.p_permutation"),
     "den": ("task_b_permutation.json",
             "arenas.in-sample.models.teacher-forced armB.368.p_binomial_two_sided"),
     "stated_orders": 13},
    # ---- C5 arena / horizon provenance (A1) ------------------------------
    {"id": "C5.1", "kind": "cell", "where": "12",
     "says": "inversely on every one of",
     "cell": ("task_b_permutation.json",
              "arenas.all-episodes.models.released aleatoric.368"),
     "expect_observed": 0, "expect_n": 45},
    {"id": "C5.2", "kind": "cell", "where": "5.5",
     "says": "negatively correlated with error on",
     "cell": ("task_b_permutation.json",
              "arenas.out-of-sample.models.released aleatoric.368"),
     "expect_observed": 20, "expect_n": 45},
    {"id": "C5.3", "kind": "cell", "where": "5.2",
     "says": "of 45 at h=1, with mean r",
     "cell": ("task_b_permutation.json",
              "arenas.all-episodes.models.released EPISTEMIC.1"),
     "expect_observed": 44, "expect_n": 45},

    # ---- coverage beyond the six defects the review named ----------------
    # None of these was reported wrong. They are guarded because the same class
    # of error -- a correct number in a wrong relation -- is what this checker
    # exists for, and a checker covering only known failures protects nothing
    # that has not already been fixed.
    {"id": "C2.3", "kind": "extremum", "where": "5.5",
     "says": "it has the largest mean correlation of the four",
     "family": ("task1_calibration.json", "cal_mean_r"),
     "named": {"label": "teacher-forced armB"}, "expect": "max"},
    {"id": "C2.4", "kind": "extremum", "where": "5.6",
     "says": "it is the largest anywhere in this work",
     "family": ("task_d_nind20.json", "d2_epistemic_r"),
     "named": {"h": "1"}, "expect": "max"},
    {"id": "C2.5", "kind": "extremum", "where": "5.2",
     "says": "the smallest is faithful (mse) h=368",
     "family": ("task_b_permutation.json", "holm_all"),
     "named": {"label": "faithful (mse) h=368"}, "expect": "min"},
    {"id": "C3.4", "kind": "compare", "where": "5.5",
     "says": "It does not beat Arm B's head on strength either",
     "a": ("task_b2_epistemic.json", "by_horizon.368.epistemic.corr_mean"),
     "b": ("task1_calibration.json", "teacher-forced armB.sigma_err_corr_mean"),
     "expect": "lt"},
    {"id": "C3.5", "kind": "compare", "where": "5.5",
     "says": "which already exceeds the smallest Holm threshold",
     "a": ("task_b_permutation.json", "arenas.out-of-sample.p_floor"),
     "b": ("task_b_permutation.json", "arenas.out-of-sample.holm.smallest_threshold"),
     "expect": "gt"},
    {"id": "C3.6", "kind": "compare", "where": "9",
     "says": "very nearly a perfect ranking. Over the full",
     "a": ("task_d_nind20.json", "d2_forecast_index.1.r_epistemic"),
     "b": ("task_d_nind20.json", "d2_forecast_index.368.r_epistemic"),
     "expect": "gt"},
    {"id": "C7.1", "kind": "count-consistency", "where": "1 / abstract / 8",
     "label": "numbered retractions",
     "says": "numbered claims in this work are withdrawn",
     "value": ("paper_numbers.json", "n_retractions.value"),
     "sites": ["numbered claims in this work are withdrawn",
               "retractions of our own numbered claims",
               "retractions on our own evidence"]},
    {"id": "C7.2", "kind": "count-consistency", "where": "1 / abstract / 8",
     "label": "framing retractions",
     "says": "further retractions withdraw framings rather than numbers",
     "value": ("paper_numbers.json", "n_retract_framing.value"),
     "sites": ["further retractions withdraw framings rather than numbers",
               "more that withdraw framings rather than numbers",
               "that withdraw framings rather than numbers"]},
    {"id": "C6.1", "kind": "relvar", "where": "4",
     "says": "Teacher forcing is more than twice as variable across seeds",
     "a": ("task_d1_threeseed.json", "aggregate.A.sd_ddof1", "aggregate.A.mean"),
     "b": ("task_d1_threeseed.json", "aggregate.B.sd_ddof1", "aggregate.B.mean"),
     "at_least": 2.0},
]


# ------------------------------------------------------------------ helpers
def _family(spec):
    """Return {label: value} for an extremum family."""
    name, kind = spec
    if kind == "d3_cells":
        D3 = art(name); T = D3["target_coverage"]
        return {f'{q}|h={f["h"]}|ep{f["fit_episode"]}': abs(f["coverage_after"] - T)
                for q in D3["quantities"] for f in D3["quantities"][q]["fits"]}
    if kind == "cal_mean_r":
        C = art(name)
        return {k: C[k]["sigma_err_corr_mean"] for k in C
                if isinstance(C[k], dict) and "sigma_err_corr_mean" in C[k]}
    if kind == "d2_epistemic_r":
        D = art(name)
        return {f"h={h}": D["d2_forecast_index"][h]["r_epistemic"]
                for h in ("1", "8", "32", "128", "368")}
    if kind == "holm_all":
        P = art(name)
        return {st["cell"]: st["p"] for st in P["arenas"]["all-episodes"]["holm"]["steps"]}
    if kind == "d2_paired_lo":
        D = art(name)
        return {f'h={h}': D["d2_forecast_index"][h]["paired_ci_lo"]
                for h in ("8", "32", "128", "368")}
    raise ValueError(kind)


def _label(named):
    """The family key the paper's sentence names.

    Three shapes, because the three families are keyed differently: a d3 cell, a
    bare horizon, and a family whose keys are already free-form labels (model
    names, Holm cells). The last needs `label`, not `h` -- overloading `h` for it
    produced "h=teacher-forced armB", which matched nothing and failed two checks
    whose underlying extremum was correct.
    """
    if "quantity" in named:
        return f'{named["quantity"]}|h={named["h"]}|ep{named["fit_episode"]}'
    if "label" in named:
        return named["label"]
    return f'h={named["h"]}'


def evaluate(c, paper, override=None):
    """Return (ok, detail). `override` corrupts the expectation, for --self-test."""
    exp = dict(c)
    if override:
        exp.update(override)

    said = exp["says"] in paper
    if not said and not exp.get("optional"):
        return False, f'the paper does not contain "{exp["says"][:48]}"'

    k = exp["kind"]
    if k == "overlap":
        a, b = dig(*exp["a"]), dig(*exp["b"])
        ov = not (a["hi"] < b["lo"] or b["hi"] < a["lo"])
        want = exp["expect"] == "overlap"
        return ov == want, (f'[{a["lo"]:.5f},{a["hi"]:.5f}] vs [{b["lo"]:.5f},{b["hi"]:.5f}] '
                            f'-> {"overlap" if ov else "disjoint"}, expected {exp["expect"]}')
    if k == "extremum":
        fam = _family(exp["family"])
        want = max(fam, key=fam.get) if exp["expect"] == "max" else min(fam, key=fam.get)
        lab = _label(exp["named"])
        return want == lab, (f'{exp["expect"]} of {len(fam)} is {want} ({fam[want]:.5g}); '
                             f'paper names {lab} ({fam.get(lab, float("nan")):.5g})')
    if k == "sign":
        a, b = dig(*exp["a"]), dig(*exp["b"])
        got = "rise" if b > a else ("fall" if b < a else "flat")
        return got == exp["expect"], (f'{a:.5f} -> {b:.5f} is a {got} of {abs(b-a):.5f}, '
                                      f'text says {exp["expect"]}')
    if k == "count-consistency":
        # One count, asserted in several places, in words or numerals. A1 was this
        # failure: section 1 said six claims were withdrawn "one of them" about
        # pre-registration, while section 8 said six numbered PLUS two framings and
        # that the pre-registration one was explicitly not among the six. Both
        # sentences were internally coherent and they contradicted each other, and
        # it survived three rounds of editing because no numeral was wrong.
        want = exp.get("_forced", dig(*exp["value"]))
        forms = {str(want), WORDS.get(int(want), ""), WORDS.get(int(want), "").lower()}
        forms.discard("")
        missing = [frag for frag in exp["sites"]
                   if not any(f"{frag} {f}" in paper or f"{f} {frag}" in paper
                              or (frag in paper and any(f in _window(paper, frag) for f in forms))
                              for f in forms)]
        return not missing, (f'{exp["label"]} = {want} ({"/".join(sorted(forms))}); '
                             f'{len(exp["sites"]) - len(missing)}/{len(exp["sites"])} sites agree'
                             + (f'; disagreeing: {missing}' if missing else ''))
    if k == "compare":
        a, b = dig(*exp["a"]), dig(*exp["b"])
        got = "gt" if a > b else ("lt" if a < b else "eq")
        return got == exp["expect"], f'{a:.6g} vs {b:.6g} -> {got}, text says {exp["expect"]}'
    if k == "relvar":
        # relative sd of b against relative sd of a, e.g. "more than twice as
        # variable across seeds" -- neither relative sd is stored, so both are
        # formed here from the mean and sd the artifact does store
        A, B = exp["a"], exp["b"]
        ra = dig(A[0], A[1]) / dig(A[0], A[2])
        rb = dig(B[0], B[1]) / dig(B[0], B[2])
        r = rb / ra
        return r >= exp["at_least"], (f'relative sd {rb:.4f} vs {ra:.4f} -> {r:.3f}x, '
                                      f'text implies at least {exp["at_least"]}x')
    if k == "orders":
        ratio = dig(*exp["num"]) / dig(*exp["den"])
        got = round(math.log10(abs(ratio)))
        if exp["stated_orders"] is None:
            return True, f'ratio {ratio:,.1f}x quoted directly, not as orders (log10={math.log10(abs(ratio)):.2f})'
        return got == exp["stated_orders"], (f'ratio {ratio:.3g}, round(log10)={got}, '
                                             f'text says {exp["stated_orders"]}')
    if k == "cell":
        cell = dig(*exp["cell"])
        ok = (cell["observed"] == exp["expect_observed"] and cell["n_dims"] == exp["expect_n"])
        return ok, (f'{exp["cell"][1]} -> {cell["observed"]}/{cell["n_dims"]}, '
                    f'text cites {exp["expect_observed"]}/{exp["expect_n"]}')
    raise ValueError(k)


def corruption_for(c):
    """A corruption must INVERT what this claim expects, not set a fixed value.

    The first version of this table set `expect: "disjoint"` for every overlap
    check and `expect: "rise"` for every sign check. For the claims that already
    expected those, the "corruption" was a no-op and the self-test reported the
    check as MISSED -- correctly, since nothing had been corrupted. Two of eleven
    were vacuous. Inverting relative to the claim fixes it, and the extremum case
    now names a real runner-up rather than a label absent from the family, so the
    check has to reject a plausible answer rather than a nonexistent one.
    """
    k = c["kind"]
    if k == "overlap":
        return {"expect": "disjoint" if c["expect"] == "overlap" else "overlap"}
    if k == "sign":
        return {"expect": "rise" if c["expect"] == "fall" else "fall"}
    if k == "orders":
        return None if c["stated_orders"] is None else {"stated_orders": c["stated_orders"] + 1}
    if k == "cell":
        return {"expect_observed": dig(*c["cell"])["observed"] + 1}
    if k == "count-consistency":
        # corrupt the COUNT, not the path: the check must reject a paper that
        # agrees with itself on a different number than the ledger holds
        return {"_forced": int(dig(*c["value"])) + 1}
    if k == "compare":
        return {"expect": "lt" if c["expect"] == "gt" else "gt"}
    if k == "relvar":
        return {"at_least": c["at_least"] * 100}
    if k == "extremum":
        fam = _family(c["family"])
        ranked = sorted(fam, key=fam.get, reverse=(c["expect"] == "max"))
        runner_up = ranked[1]                       # the second-best, a plausible wrong answer
        if "|" in runner_up:
            q, h, ep = runner_up.split("|")
            return {"named": {"quantity": q, "h": int(h[2:]), "fit_episode": int(ep[2:])}}
        if runner_up.startswith("h=") and runner_up[2:].isdigit():
            return {"named": {"h": runner_up[2:]}}
        return {"named": {"label": runner_up}}
    raise ValueError(k)


def main():
    paper = open(PAPER).read()
    rows, bad = [], 0
    for c in CLAIMS:
        ok, detail = evaluate(c, paper)
        rows.append({"id": c["id"], "kind": c["kind"], "where": c["where"],
                     "says": c["says"], "pass": ok, "detail": detail})
        bad += not ok
    print("PART C — COMPARATIVE CLAIM CHECK")
    print("=" * 104)
    for r in rows:
        print(f"  {'PASS' if r['pass'] else 'FAIL'}  {r['id']:<6} {r['kind']:<9} §{r['where']:<18} {r['detail']}")
    print("=" * 104)
    print(f"  {len(rows) - bad}/{len(rows)} comparative claims verified")

    out = {"n_claims": len(rows), "n_pass": len(rows) - bad, "claims": rows}

    if "--self-test" in sys.argv:
        print("\n  SELF-TEST — every check must FAIL when its expectation is corrupted")
        print("  " + "-" * 100)
        st, st_bad = [], 0
        for c in CLAIMS:
            corrupt = corruption_for(c)
            # the orders check that quotes the ratio directly has no stated_orders
            # to corrupt, which is precisely why A5 was fixed that way
            if corrupt is None:
                st.append({"id": c["id"], "skipped": "quotes the ratio directly, "
                                                     "no orders claim to corrupt"})
                print(f"  n/a   {c['id']:<6} quotes the ratio directly — nothing to corrupt")
                continue
            ok, detail = evaluate(c, paper, override=corrupt)
            caught = not ok
            st.append({"id": c["id"], "corruption": str(corrupt), "caught": caught})
            st_bad += not caught
            print(f"  {'caught' if caught else 'MISSED':<6} {c['id']:<6} {detail}")
        print("  " + "-" * 100)
        n = len([x for x in st if "caught" in x])
        print(f"  {n - st_bad}/{n} corruptions caught")
        out["self_test"] = {"n": n, "caught": n - st_bad, "detail": st}
        bad += st_bad

    json.dump(out, open(os.path.join(R.RESULTS, "comparative_claims.json"), "w"), indent=2)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
