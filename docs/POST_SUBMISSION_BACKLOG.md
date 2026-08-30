# Post-submission backlog

Findings recorded and deliberately not fixed, under the closing-brief stop rule. One line
each, as found. **Nothing here is fixed.** Authorised as the single new file permitted in
Sessions 1-3 (closing brief v2, correction C-1).

- `e5_sigma_dilution.json` loses five `.null.*` keys between writers — the M-61 two-code-paths shape, in a second artifact.
- `restatement_index.json` stores `PAPER.md` line numbers, which makes a build-order-dependent artifact part of the reproducibility figure.
- `t1_bibliography_verified.json` drops twelve `n_fragments` counts, plausibly network-dependent.
- Re-running the verifier grows its self-referential exclusion list by the two keys added here. No published figure moves; verified by running it twice and diffing.
