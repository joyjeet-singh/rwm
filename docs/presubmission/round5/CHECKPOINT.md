# Round-5 checkpoint — after GT2 (2026-10-23)

**State.** Branch `presubmission5`. Last log entry: **GT2 — COMPLETE**. Nothing pushed. Pages 18.25/12, abstract 207/5.

**Next action.** `docs/presubmission/round5/go.zsh G13` (Opus 5.5, high): the uncertainty section around three gaps (§5), replacing the interim `## 5.` heading and the old §6. Read READINGS' GT2 addendum and ledger M-104 for the X11 readings; they fill OUTLINE's **[X11 slot]** marks.

**GT2 did.** Queue gate passed; X11a–e computed by the frozen scripts: X11a MIXED at h = 1 (IN-SAMPLE FLATTERS at 100, 368); X11b GENERALISES; X11c DOES NOT RESTORE CALIBRATION (72 of 180 cells; pooled coverage within band, alongside only); X11d MECHANISM SUPPORTED; X11e PROPAGATION NARROWS THE GAP. M-104 records them; five Status lines set; stages 11l and 20v3–20v7; keys `x11a_*`–`x11e_*`.

**What G13 and later must handle (rule 10).** (1) X10's "in-sample worse at h = 1" no longer holds at n = 20: say the h = 1 sign is not stable and the long-horizon label is flattering. (2) §5.7 must give X11c's cell-level reading and the pooled coverage together; no summary may drop "on the released checkpoint" (OUTLINE rule-10 row [X11c]). (3) §1's, the abstract's and contribution 4's wording ("restores one-sigma coverage on the released checkpoint") stays true as written, but the abstract's claim now needs G14's rule-10 audit against X11c. (4) Table 3 gains the fold-ensemble row; H11, H12 gain X11d and X11e.

**What G13–G15 must know (carried).** §1 and §3 point at §5.2–§5.7 by OUTLINE's numbering. The withdrawal-count gate reads §3.4. Table 1 is the arenas table; the claim-to-verdict table is G14's. §1, §3, §4 are over budget. Figure anchors (G10) use today's appendix letters. `typed_numeral_audit`: cite "Name (year)", write `$\rho$`, no bare numerals in prose; `{{key|s2}}` on a text key fails. The README template still points at old section numbers.

**Facts later sessions must not lose.** (1) `round5/READINGS.md` is the rewrite sessions' source for every new reading. (2) A key that leaves the paper on purpose goes into `round5/RETIRED_KEYS.md`, or `keys` fails at G16. (3) `LENGTH_LOG.md` counts whitespace tokens from the title to `## References`. (4) `pdftoppm` is absent: G16 must open the figure pages by eye. (5) The run records `results/x3_run_*` are committed (since G11's first commit; see the GT2 log entry).

**Blockers.** None.
