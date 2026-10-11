"""F3 item 2 (N6, post hoc): check the regenerated results/a2_trajectory_level_control.json against the committed one.

  1. Every field not derived from the difficulty measure is unchanged, to 1e-12 (numbers) or exactly (everything else).
     The difficulty-derived fields are h1_diagnostic's episode_difficulty_range, confounders.episode_difficulty_D12.*,
     partial_on_both, collapses and difficulty_source: the only fields scripts/a2_trajectory_level_control.py builds from
     `diff` (its lines 265-312).
  2. Ruling W5: no verdict string changes, and no correlation or partial changes sign. Every difficulty-derived
     correlation and partial is checked; the ones the paper reports (a2_h1_diff_r, a2_h1_partial_both) are flagged.
Writes docs/presubmission/round4/f3_n6_check.json and prints old -> new for every difficulty-derived field.
Run from the repository root, after the regeneration and before committing it:
  $PY docs/presubmission/round4/f3_n6_check.py
"""
import json
import subprocess
import sys

NEW = "results/a2_trajectory_level_control.json"
OUT = "docs/presubmission/round4/f3_n6_check.json"
old = json.loads(subprocess.run(["git", "show", f"HEAD:{NEW}"], capture_output=True, text=True, check=True).stdout)
new = json.load(open(NEW))
DERIVED = ("h1_diagnostic/episode_difficulty_range", "h1_diagnostic/confounders/episode_difficulty_D12",
           "h1_diagnostic/partial_on_both", "h1_diagnostic/collapses", "h1_diagnostic/difficulty_source")
REPORTED = {"h1_diagnostic/confounders/episode_difficulty_D12/r_disagreement_vs_confounder": "a2_h1_diff_r",
            "h1_diagnostic/partial_on_both": "a2_h1_partial_both"}


def leaves(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, f"{path}/{k}" if path else str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, f"{path}[{i}]")
    else:
        yield path, o


lo, ln = dict(leaves(old)), dict(leaves(new))
assert lo.keys() == ln.keys(), sorted(set(lo) ^ set(ln))
derived = lambda p: any(p == d or p.startswith(d + "/") or p.startswith(d + "[") for d in DERIVED)
changed_other, changes, sign_flips, verdicts = [], {}, [], []
for p in lo:
    a, b = lo[p], ln[p]
    num = isinstance(a, (int, float)) and not isinstance(a, bool) and isinstance(b, (int, float)) and not isinstance(b, bool)
    same = (abs(a - b) <= 1e-12) if num else (a == b)
    if derived(p):
        if not same:
            changes[p] = [a, b]
            # correlations and partials only: the range is a span of positive values, and shrinkage is a difference
            # of two correlations (reported above, not a correlation itself)
            if num and (a > 0) != (b > 0) and "range" not in p and not p.endswith("shrinkage"):
                sign_flips.append(p)
            if isinstance(a, (str, bool)) and p != "h1_diagnostic/difficulty_source":
                verdicts.append(p)
    elif not same:
        changed_other.append(p)
ok1 = not changed_other
ok2 = not sign_flips and not verdicts
rec = {"what": "N6: the regenerated a2 artifact against the committed one", "n_leaves": len(lo),
       "derived_fields": list(DERIVED), "non_derived_unchanged": ok1, "non_derived_changed": changed_other,
       "derived_changes": changes, "sign_flips": sign_flips, "verdict_changes": verdicts,
       "reported_in_paper": REPORTED, "ruling_W5_passes": ok2}
json.dump(rec, open(OUT, "w"), indent=1)
print(f"  {len(lo)} leaves; non-derived unchanged to 1e-12: {ok1}" + ("" if ok1 else f" -- CHANGED: {changed_other[:10]}"))
for p, (a, b) in changes.items():
    print(f"  {p}{' (paper: ' + REPORTED[p] + ')' if p in REPORTED else ''}: {a!r} -> {b!r}")
print(f"  ruling W5: sign flips {sign_flips or 'none'}; verdict changes {verdicts or 'none'} -> {'PASS' if ok2 else 'BLOCKED'}")
sys.exit(0 if ok1 and ok2 else 1)
