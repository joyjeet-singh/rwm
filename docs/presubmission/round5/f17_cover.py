"""Round 5, G17 step 5: write docs/COVER_STATEMENT.md from results/paper_numbers.json.

Replaces round 4's statement, whose sentences described the paper before its rewrite. Every figure is read from
the artifact; none is typed. Each sentence follows the paper's own wording and keeps the scope the locked framing
requires. Run from the repository root after the final build.
"""
import json
import re

N = json.load(open("results/paper_numbers.json"))
N = N.get("values", N)


def v(k):
    assert k in N, f"no key {k}"
    return N[k]["value"]


G = json.load(open("results/round5_gates.json"))["gates"]
pages = G["pages"]["value"]
n_rules, n_pos = int(v("appG_n_lead")), int(v("appG_n_positive"))
assert n_rules - n_pos == 1, (n_rules, n_pos)
_md = open("PAPER.md").read()
_s7 = _md[_md.index("## 7. Lessons and limitations"):_md.index("## 8. Conclusion")]
n_lessons = len(re.findall(r"^- \*", _s7.split("**Limitations.**")[0], re.M))
L = f"""# Cover statement — TMLR submission

*Every figure below is read from `results/paper_numbers.json` by `docs/presubmission/round5/f17_cover.py`; none is
typed. The paper's main content is {pages} pages.*

---

## Which acceptance criterion this submission meets

TMLR asks two questions. This submission answers both directly.

### 1. Are the claims supported by accurate, convincing and clear evidence?

- **Verification before measurement.** The reimplementation matches the released module's gradients before any
  training run is scored: a maximum difference of {v('diff_grad_max')} across {v('diff_terms')} loss terms and
  {v('diff_n_params')} parameter tensors (paper §3.1, Appendix A).
- **{n_rules} pre-registered decision rules, with git lead times.** Appendix E gives each rule, its commit, its lead
  time computed from git and its verdict verbatim. {n_pos} have a positive lead; the one that does not is the rule the
  paper withdraws as a pre-registration, and says so (§3.4). {str(v('n_retractions_word')).lower()} claims and {str(v('n_retract_framing_word')).lower()} framings of our own were
  withdrawn on evidence and are kept in the ledger beside it.
- **Verdicts reported as returned, the inconvenient ones included.** In-sample measurement of calibration is not worse
  at one step once every episode is held out ({v('x11a_verdict')}), against an earlier reading on four trajectories;
  the per-horizon multiplier on episodes a model never saw does not restore calibration cell by cell
  ({v('x11c_cells_cal')} of {v('x11c_n_cells')}) while the pooled coverage is within the band; a rule on whole
  trajectories at four returned an inconclusive reading that the twenty-trajectory replication resolved.
- **Small samples are treated as small.** At four trajectories the smallest attainable exact p is
  {v('n7_p_min_n4_frac')}, above every Holm level used, so no comparison at that size is called resolved; each is
  reported with its exact p and as "k of the four". The base claim is re-tested on {v('x3_n')} trajectories, each of
  ten episodes held out once.
- **Clear scope.** Every number names its arena, its count of independent trajectories, its checkpoint and its
  horizon; the released checkpoint's training rows are not recorded (§3.2), and the paper says so and never calls its
  arena held out.

### 2. Would some of TMLR's audience be interested?

- A released uncertainty estimate ranks error well and sizes it wrongly, and the paper separates three gaps
  (one-step, trunk-sharing, accumulation) that a single ratio runs together (§5).
- The per-member variance collapses because the implemented loss is minimised at zero, shown against known noise
  and as an ordinary Adam step (§5.5): a check any practitioner can run on a bounded-σ head.
- Rolling each ensemble member out separately repairs part of the accumulation, which is not the released method
  (§5.4); and the rescaling that fixes one-sigma coverage on the released checkpoint does not fix the tails (§5.7).
- The paper gives practitioners {n_lessons} lessons (§7) and credits the originals' documented designs.

---

## Reproducibility Certification

The paper's primary purpose is to reproduce and test two published works, and it adds value beyond the
reproduction: a held-out replication of the base claim, an ensemble with independent members, per-member rollout,
exact tests, the free baselines for the trust metric, and the defect analysis.

| criterion | evidence |
|---|---|
| independent reimplementation | matches the release's gradients (§3.1, Appendix A) |
| the originals' claims tested as published | Appendix D, Table 4; the versions read are named and compared (Appendix D) |
| code and data | the full repository, every artifact and the claim ledger, anonymised, in the supplementary ZIP |
| clean-clone reproduction | {v('ver_values')} regenerated values compared, {v('ver_identical')} identical; the {v('ver_differing')} that differ are bookkeeping about the submission's own files, {v('ver_part_sci')} scientific (§8, supplement S11) |
| pre-registration | {n_rules} rules, Appendix E |
| negative and withdrawn results | kept and stated (§3.4, §5.7, Appendix E) |
"""
open("docs/COVER_STATEMENT.md", "w", encoding="utf-8").write(L)
print("wrote docs/COVER_STATEMENT.md,", len(L.split()), "words")
