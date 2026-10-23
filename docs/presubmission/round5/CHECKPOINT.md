# Round-5 checkpoint — after G11 (2026-10-23)

**State.** Branch `presubmission5`. Last log entry: **G11 — COMPLETE**. Nothing pushed. Pages 21.92/12, abstract 207/5.

**Next action.** `docs/presubmission/round5/go.zsh G12` (Opus 5.5, high): the base paper's claims (§4). GT2 (queue shows 20 of 20, none failed) runs after G12, then G13. Never read the X11 evaluations before GT2.

**G11 did.** New title, abstract, §1, §2, §3 (Table 1 = arenas) and a 85-word "Reproducibility and data" at the end; the earlier text is verbatim in supplementary S13–S18 (S13 title and abstract, S14 §1, S15 §2, S16 §3, S17 §8, S18 Data and code). The old §8 no longer exists: pointers to it read §3.4, and §3.4 holds the pre-registration paragraph and the three withdrawal counts (the `check_retraction_counts` gate now reads §3.4).

**What G12–G15 must know.** (1) §1–§3 point at §4.1–§4.3, §5.2–§5.7, §6, §7 and Appendices A, B, E, J, L, O by OUTLINE's numbering; they resolve as those sections are written. (2) The old §4 ("What the original papers claim") is still in place for G12 to rewrite; its sentence about "§5" and "§6" are the old numbers. (3) Table 1 is the arenas table; the claim-to-verdict table (OUTLINE §Referee 13) is G14's. (4) §1 and §3 are over their word budgets; G14 trims. (5) G10's figure anchors still use today's appendix letters. (6) `typed_numeral_audit.py` has a `table-ref` class; a citation list must be written "Name (year), Name (year)" because the audit reads only a year followed by ")". (7) `ρ` must be `$\rho$` in the template (the LaTeX converter rejects the Unicode letter). (8) A `{{key|s2}}` number counts toward the abstract's five numerals each time it appears.

**Queue status** (repository root): `echo "done $(wc -l < runs/queue_round5_done.txt) of 20; failed $(wc -l < runs/queue_round5_failed.txt)"; tail -n 2 runs/queue_round5.log`. `results/x3_run_*_ens5.json` and `x3_run_*_seed*.json` stay uncommitted until GT2.

**Facts later sessions must not lose.** (1) M-97–M-100 and M-103 are discharged in GT2 by frozen scripts. (2) GT2 adds the X11 stages. (3) `round5/READINGS.md` is the rewrite sessions' source for every new reading. (4) A key that leaves the paper on purpose goes into `round5/RETIRED_KEYS.md`, or `keys` fails at G16. (5) `LENGTH_LOG.md` counts whitespace tokens from the title to `## References`. (6) `pdftoppm` is absent: G16 must open the figure pages by eye. (7) The moved figures' captions are still the old long ones.

**Blockers.** None.
