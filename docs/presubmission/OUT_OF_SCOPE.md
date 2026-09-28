# Out of scope — noticed, not fixed

One line per item: `file:line — what was noticed — session that noticed it`. Plan §1.1: a session
records here anything outside its own tasks and does not fix it, however quick the fix.

---
- `scripts/build_supplementary.py:55,172` and `scripts/make_anon_bundle.py:393` — both bundle builders walk `docs/` recursively, so everything in `docs/presubmission/` (this plan, the session log, and S3's `AUTHOR_QUERY_ALIGNMENT.md`) will ship in both reviewer bundles unless it is added to their `EXCLUDE` sets, which already exclude the other author-contact documents (`build_supplementary.py:79-80`, `make_anon_bundle.py:333-334`). S0's files carry no deny-list string (checked against `t5_anon_transcript.py:68`'s `DENY`: 0 hits). — S0
- `reproduce.sh:158-168` — the full-run training block drives `run_remaining.sh`, `run_10k.sh`, `run_tasks45.sh`, `run_control.sh` and `run_ens5.sh`. No stage drives `run_10k_d1.sh`, `run_indep_ens.sh`, `run_m49_matched.sh`, `run_nll.sh` or `run_nll_indep_ens.sh`. Not checked whether this is deliberate. — S0
- `PAPER.template.md.appbak` (repo root) — tracked in git, while the sibling `*.t2bak`, `*.c2bak`, `*.t3bak` and `*.t4bak` backups are ignored (`.gitignore:44-50`). — S0
