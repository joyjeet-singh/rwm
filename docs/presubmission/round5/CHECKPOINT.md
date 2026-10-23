# Round-5 checkpoint — after G10 (2026-10-23)

**State.** Branch `presubmission5`. Last log entry: **G10 — COMPLETE**. Nothing pushed. Pages 24.0/12 (G11–G15 bring it down).
The X11 queue's done file showed **20 of 20** at the start of G10; confirm with the status command below and check `runs/queue_round5_failed.txt` before GT2.

**Next action.** GT2 (`go.zsh GT2`, Sonnet 5.5, medium) first if Y5 is B or C (PLAN §0.4 order puts it between G12 and G13; check §0.4), else G11. Never read the X11 evaluations before GT2.

**G10 did.** New Figure 1 (X3 by episode; X9's error-to-spread) and recast Figure 2 (σ bounds and the Adam signature) in `scripts/paper_figures.py`; the six older figures moved to appendices; `build_paper.py` places figures by `ANCHOR` headings and numbers them in document order (1–8). Prose references remapped. **The anchors use today's appendix letters (E, J, K, L, M, Q), not OUTLINE's A–O: G15 must move them when it re-letters.** OUTLINE's "Figure 3" (rescaling by horizon, §5.7) is not drawn: G10's items do not list it; G13 draws it.

**Queue status** (repository root): `echo "done $(wc -l < runs/queue_round5_done.txt) of 20; failed $(wc -l < runs/queue_round5_failed.txt)"; tail -n 2 runs/queue_round5.log`.
`results/x3_run_*_ens5.json` and `x3_run_*_seed*.json` stay uncommitted until GT2.

**Facts later sessions must not lose.** (1) M-97–M-100 and M-103 are discharged in GT2 by frozen scripts. (2) GT2 adds the X11 stages. (3) `round5/READINGS.md` is the rewrite sessions' source for every new reading. (4) A key that leaves the paper on purpose goes into `round5/RETIRED_KEYS.md`, or `keys` fails at G16. (5) `LENGTH_LOG.md` counts whitespace tokens from the title to `## References`. (6) A build ends dirty on `PAPER.pdf`: commit it when content changed, `git restore` it when only the date did. (7) `pdftoppm` is not installed, so rendered pages cannot be viewed here; G16 must open the figure pages (2, 14, 37, 42, 45, 47, 50, 58) by eye. (8) The moved figures' captions are still the old long ones.

**Blockers.** None.
