# S0 baseline — build and checks at `pre-presubmission` (da74907)

Recorded 2026-09-28 by session S0, on the working tree at tag `pre-presubmission`
(da7490768392d251c12dc08f4124eb4ba72a8b92), before any pre-submission edit. Nothing was fixed.
This is the "before" that S11 compares against. Interpreter: the absolute path of
`PDM/.venv-rwm311/bin/python` (written `$PY` below; see `FILE_MAP.md`), run from the repository
root.

## Sequence run

Fast build, then the gates, then the fast build a second time, to confirm a fixed point:

1. `$PY scripts/paper_numbers.py` → `$PY scripts/build_paper.py` → `$PY scripts/build_model_card.py`
   → `$PY scripts/build_readme.py` → `$PY scripts/compile_paper.py`
2. `$PY scripts/ledger_check.py`, `$PY scripts/check_comparative_claims.py --self-test`,
   `$PY scripts/typed_numeral_audit.py`, `$PY scripts/restatement_index.py`,
   `$PY scripts/horizon_sweep.py`, `$PY scripts/xref_sweep.py`, `$PY scripts/check_scope_audit.py`,
   `$PY scripts/pdf_render_check.py`
3. Step 1 again.
4. Once, separately: `$PY scripts/part_f_gate.py` and `$PY scripts/submission_check.py`, with
   `RWM_IDENT` = full name, git-log email and handle, and `RWM_IDENT_REPO` = the repository URL.
   That is the configuration the verification tail used (`docs/DEFERRED.md:191`).
   `CLONE_RESULTS` was not set.

Wall clock: 51 s for steps 1–3, 7 s for step 4. No job ran over 1 minute.

## Result per check

| Check | Exit | Result at baseline |
|---|---:|---|
| `paper_numbers.py` | 0 | wrote `results/paper_numbers.json`, byte-identical to committed |
| `build_paper.py` | 0 | no unresolved placeholder; converter gate self-test 4 of 4; prints "numerals typed in prose: 132" |
| `build_model_card.py` | 0 | `MODEL_CARD.md` byte-identical to committed (needs local `runs/`) |
| `build_readme.py` | 0 | `README.md` byte-identical to committed |
| `compile_paper.py` | 0 | PASS — 48 pages, 1,024,202 bytes, 0 errors, 0 overfull, 0 underfull, 0 LaTeX warnings |
| `ledger_check.py` | 0 | PASS — 254 entries, 99 CONTRIB, 0 lacking evidence, 0 missing artifacts, 0 undischarged rules, 6 supersessions, 0 unreflected retractions, RESULTS.md table current |
| `check_comparative_claims.py --self-test` | 0 | PASS — 60/60 comparative claims verified; 60/60 corruptions caught |
| `typed_numeral_audit.py` | 0 | PASS — self-test caught planted 12.7; 686 typed numerals, all classified (18 classes, 23 exceptions) |
| `restatement_index.py` | 0 | PASS — no typed restatements; no ambiguous numerals |
| `horizon_sweep.py` | 0 | PASS — 0 findings (grid 1, 8, 32, 100, 128, 368; h = 100 deployment, h = 368 diagnostic) |
| `xref_sweep.py` | 0 | PASS — 63 pointers: 61 ok, 2 reviewed, 0 unverified, 0 suspect |
| `check_scope_audit.py` | 0 | PASS — 27 kinds (18 whole-file, 4 named-region, 5 artifact-only), 0 unclassified |
| `pdf_render_check.py` | 0 | PASS — 5/5 |
| `part_f_gate.py` | 0 | 7/7 run checks pass; check 4 NOT RUN locally (needs `CLONE_RESULTS`). The committed record `results/part_f_gate.json` holds check 4 **failing** on 365 differing values (clone C), as published; the local run's rewrite of that file was restored |
| `submission_check.py` | 1 | 20/22 — PENDING E7 (excluded artifact named, absent from template) and C1 (431 claims: 196 SUPPORTED, 235 UNREVIEWED). Both are recorded as known (`docs/SUBMISSION_CHECKLIST.md`) |

## Byte-identity

`PAPER.md`, `PAPER.tex`, `MODEL_CARD.md`, `README.md`, `docs/BUILD_CHECKS.md` and
`results/paper_numbers.json` were identical across the committed tree, build 1 and build 2
(SHA-256). `PAPER.pdf` differs on every compile. With `/CreationDate`, `/ModDate` and `/ID`
blanked, the rebuilt PDF equals the committed one (1,024,084 bytes each after blanking). The only
tracked files any step changed were `PAPER.pdf` and `results/part_f_gate.json`, and both were
restored with `git checkout`.

| File | SHA-256 (committed = build 1 = build 2) |
|---|---|
| `PAPER.md` | `c95f907fcdc80d63990165a2b4bbea4fd86542092cb1daadb0e83dc2314a178f` |
| `PAPER.tex` | `494a493822615524bd872e0573cc9d6aee832d14b4c2867f426cd2b6d451a6b1` |
| `MODEL_CARD.md` | `a0f6ffe68314cda6c7b23491c172fff34c2c4ba8851c6b93d5e86aa3ec5a1a33` |
| `README.md` | `935d8ac16874e9cb0913f8f160fc16112ae71666af5da55864a61c36b940d0df` |
| `docs/BUILD_CHECKS.md` | `eca4048227c55692af2939090921191fe85598d5fe10a9da9d0d5dc1a4b28813` |
| `results/paper_numbers.json` | `c53854758dda43b47eba83ee4bf242cde17294d3338a77955c9fcebc9e5aed2f` |
| `PAPER.pdf` (committed; differs per compile) | `2e2b0bf7dc5832cd9b989529a755e19b7e7eee6739cdeb9d12e268a361c49974` |
