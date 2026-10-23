# Round-5 checkpoint — after G13 (2026-10-23)

**State.** Branch `presubmission5`. Last log entry: **G13 — COMPLETE**. Nothing pushed. **Pages 13.1/12**, abstract 207/5, 8,919 body words.

**Next action.** `docs/presubmission/round5/go.zsh G14` (Opus 5.5, medium): defects, lessons, limitations, conclusion and statements; reach 12 pages. The current §7 (defects), §9 (lessons), §11 (limitations), §12 (conclusion) are still the earlier text and are numbered as before; G14 rewrites them into §6–§8 and cuts the remaining ~1.1 pages (§1, §3, §4, §5 are over their budgets by about 400, 300, 135 and 660 words).

**G13 did.** New §5 (5.1–5.7) in OUTLINE's order; old §6 is supplementary S20–S27. X11's readings are in 5.2 (MIXED at h = 1), 5.3 (independent members at n = 20), 5.4 (X11e), 5.6 (X11b) and 5.7 (X11c, both faces). The checker found no numeric mismatch.

**What G14 must handle.** (1) Rule 10 on summaries: the abstract and contribution 4 say "rescaling restores one-sigma coverage on the released checkpoint" (true) but X11c's cell-level reading on the folds says no; §7 lessons and limitations must say both. In-sample: no summary may say in-sample is worse at h = 1. (2) The old §7–§12 numbers: §1's pointers to the defects section and the limitations are words; restore numbers when the sections exist. (3) The claim-to-verdict table (OUTLINE §Referee 13) and the old §4's tested/untested counts (supplementary S19). (4) **Figure 3 is undrawn** (see session log); decide. (5) The README template still points at old section numbers.

**Carried facts.** The withdrawal-count gate reads §3.4. Figure anchors use today's appendix letters. `typed_numeral_audit`: cite "Name (year)", `$\rho$`, no bare numerals in prose, "§6" must have a heading. `{{key|s2}}` on a text key fails. `pdf_render_check` needs a heading for every top-level section number the text points at. `pdftoppm` is absent: G16 must open the figure pages by eye. A key that leaves the paper on purpose goes into `round5/RETIRED_KEYS.md`. `scripts/a1_consent_letter.py`'s fallback rewrites no longer match (OUT_OF_SCOPE, G15).

**Blockers.** None.
