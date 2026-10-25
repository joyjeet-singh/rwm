# rwm_analysis — the earliest analysis of the dataset

This folder is the first work on the released state–action dataset
(`robotic_world_model_lite/assets/data/state_action_data_0.csv`), written before this repository existed:

- `analyze_state_action_data.py` writes `report.txt` and the four plots in `figures/`;
- `verify_resets.py` tests whether rows 999, 1999, …, 9999 are unmarked episode resets;
- `diagnose_jump.py` locates every large jump between adjacent rows.

**Added to the repository on 25 October 2026**, after round 5's frozen submission files were built. Until then it
lived beside the repository and was not tracked. Ledger entry X-09 in `FINDINGS_LEDGER.md` was written while it was
untracked and says so: it audits this folder and maps every early finding to the ledger entry that now carries it
(D-03 to D-09). Nothing here is cited by the paper, and no stage of `reproduce.sh` runs it.

**Changes from the originals:** only paths. The two short scripts read the CSV from
`~/Downloads/PDM/robotic_world_model_lite/` instead of an absolute home path, and `report.txt` prints `$HOME` where
it printed that path. `analyze_state_action_data.py` looks for the upstream checkout next to its own parent folder.
From here, pass the CSV explicitly:

```
python rwm_analysis/analyze_state_action_data.py --csv <path to robotic_world_model_lite>/assets/data/state_action_data_0.csv
```
