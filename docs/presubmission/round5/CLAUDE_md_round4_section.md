## Finishing round 4: the TMLR workplan (adopted 16 Oct 2026)

`rwm_repro/docs/presubmission/round4/TMLR_CODEX_WORKPLAN.md` is the user's handoff for
sessions F5 to F12 and the TMLR package. Read it with `round4/PLAN.md` §1 and the active
session's section. It does not amend PLAN's decision rules. Where the two differ on
process, the workplan wins:

- **No external actions.** Do not push, merge, upload (Hugging Face), archive or submit.
  Commit locally and leave publication to the user. This replaces PLAN §1.4's push at
  the end of each session.
- **Delegation.** Do routine reading, queue work, measurements, edits and decisions
  yourself. F10 is the one planned multi-agent review: at most two read-only reviewers,
  one for Appendices A–M and one for N onward. Each gets only its range and the
  artifacts it cites, and reports mismatches only (file:line, at most 300 words).
  Verify every finding yourself.
- **Context.** Per phase, read the workplan, PLAN §1, that phase's section, the last
  SESSION_LOG entry and the annexes it names. Leave a checkpoint of at most 1,000
  tokens at each phase boundary.
- **Locked framing** (workplan §3):
  - X3's outcome goes in the abstract and contribution 2, whatever it is (W11);
  - X4 tests parameter count only;
  - X5 stays NOT RUN, and the command is never inferred from achieved velocity;
  - X6 is the short-unit h = 100 result, not the 400-step h = 368 one;
  - X7 is pooled epistemic coverage, on a checkpoint that trained on all ten episodes;
  - X8 covers its four rules only;
  - N5 and N6 stay post hoc.
- **No new training.** The workplan's optional inference-only sensitivities (§5) each
  need four things before they run: a protocol and script written first, a
  reproduction assertion, a separate artifact and stage, and a timing estimate.
- **TMLR checks at F7 and F11.** Verify the current official author instructions
  (length, template, anonymity, supplement, author quotas) before treating any word
  target as a venue limit. The user ruled on 16 Oct (workplan addendum) that the
  ≤16,000-word target is editorial, not a venue cap: TMLR allows any length (as read
  on 14 Oct). No LLM-use footnote was adopted.
