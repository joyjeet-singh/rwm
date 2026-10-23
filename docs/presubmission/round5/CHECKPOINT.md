# Round-5 checkpoint — after G12 (2026-10-23)

**State.** Branch `presubmission5`. Last log entry: **G12 — COMPLETE**. Nothing pushed. Pages 18.25/12, abstract 207/5.

**Next action.** `docs/presubmission/round5/go.zsh GT2` (Sonnet 5.5, medium): the X11 readings and the training gate (PLAN §0.4: GT2 follows G12; the queue showed 20 of 20, none failed). Then G13. Never read the X11 evaluations before GT2.

**G12 did.** New §4 (4.1 fold replication led, one-step reversal, 10k factor as support; 4.2 one paragraph; 4.3 with Table 2). Old §4 and §5 are verbatim in supplementary S19. 66 pointers to the old §5.x now read §4.1/§3.2/§4.2/§4.3. The uncertainty section (old §6, headings still 6.1–6.8) sits under an interim `## 5.` heading that **G13 must replace**; old pointers to §6.x still resolve to those headings.

**What G13–G15 must know.** (1) §1 and §3 point at §5.2–§5.7 by OUTLINE's numbering. (2) The `check_retraction_counts` gate reads §3.4. (3) Table 1 is the arenas table; the claim-to-verdict table is G14's. (4) §1, §3, §4 are over their word budgets. (5) Figure anchors (G10) use today's appendix letters. (6) `typed_numeral_audit`: cite as "Name (year)", write `$\rho$`, avoid a bare "1" or "8" in prose. (7) A `{{key|s2}}` on a text key fails: use the bare key. (8) The README template still points at the old section numbers (13 references): G17 or G15.

**Queue status** (repository root): `echo "done $(wc -l < runs/queue_round5_done.txt) of 20; failed $(wc -l < runs/queue_round5_failed.txt)"; tail -n 2 runs/queue_round5.log`. `results/x3_run_*_ens5.json` and `x3_run_*_seed*.json` stay uncommitted until GT2.

**Facts later sessions must not lose.** (1) M-97–M-100 and M-103 are discharged in GT2 by frozen scripts. (2) GT2 adds the X11 stages. (3) `round5/READINGS.md` is the rewrite sessions' source for every new reading. (4) A key that leaves the paper on purpose goes into `round5/RETIRED_KEYS.md`, or `keys` fails at G16. (5) `LENGTH_LOG.md` counts whitespace tokens from the title to `## References`. (6) `pdftoppm` is absent: G16 must open the figure pages by eye.

**Blockers.** None.
