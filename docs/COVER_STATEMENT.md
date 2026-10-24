# Cover statement — TMLR submission

*Every figure below is read from `results/paper_numbers.json` by `docs/presubmission/round5/f17_cover.py`; none is
typed. The paper's main content is 11.67 pages.*

---

## Which acceptance criterion this submission meets

TMLR asks two questions. This submission answers both directly.

### 1. Are the claims supported by accurate, convincing and clear evidence?

- **Verification before measurement.** The reimplementation matches the released module's gradients before any
  training run is scored: a maximum difference of 0.000e+00 across 7 loss terms and
  106 parameter tensors (paper §3.1, Appendix A).
- **35 pre-registered decision rules, with git lead times.** Appendix E gives each rule, its commit, its lead
  time computed from git and its verdict verbatim. 34 have a positive lead; the one that does not is the rule the
  paper withdraws as a pre-registration, and says so (§3.4). nine claims and eight framings of our own were
  withdrawn on evidence and are kept in the ledger beside it.
- **Verdicts reported as returned, the inconvenient ones included.** In-sample measurement of calibration is not worse
  at one step once every episode is held out (MIXED), against an earlier reading on four trajectories;
  the per-horizon multiplier on episodes a model never saw does not restore calibration cell by cell
  (72 of 180) while the pooled coverage is within the band; a rule on whole
  trajectories at four returned an inconclusive reading that the twenty-trajectory replication resolved.
- **Small samples are treated as small.** At four trajectories the smallest attainable exact p is
  1/8, above every Holm level used, so no comparison at that size is called resolved; each is
  reported with its exact p and as "k of the four". The base claim is re-tested on 20 trajectories, each of
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
- The paper gives practitioners 7 lessons (§7) and credits the originals' documented designs.

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
| clean-clone reproduction | 18,327 regenerated values compared, 18,324 identical; the 3 that differ are bookkeeping about the submission's own files, 0 scientific (§8, supplement S11) |
| pre-registration | 35 rules, Appendix E |
| negative and withdrawn results | kept and stated (§3.4, §5.7, Appendix E) |
