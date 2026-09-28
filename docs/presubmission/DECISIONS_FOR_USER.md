# Decisions for the user — pre-submission programme

A session that stops with `BLOCKED` writes its question here under its own anchor
(`## SX-<short-name>`), with the evidence and the options. The user answers under the question,
then launches the same session with `Resume session SX.`

Nothing is decided here by a session. An answer is recorded verbatim, with its date.

---

## S1-original-vs-plan

Asked in chat by S1 on 2026-09-28, before the pre-registration commit, because extracting the
original's specs (`ORIGINAL_SPECS.md`) showed three places where the plan's drafts depart from
what the original states.

1. **Rule BASE, training regime.** The original trains its baselines with teacher forcing
   (2501.10100v1 §IV-D, p. 8) and compares them against RWM-AR; PLAN S2b trains the MLP and the
   transformer autoregressively over N = 8.
   **Answer (verbatim, 2026-09-28):** "Both regimes"
2. **Baseline architectures.** The original's Table S7 (v1 p. 15) against PLAN S2b's Gaussian RSSM
   (PlaNet), learned positions and ±5% parameter matching.
   **Answer (verbatim, 2026-09-28):** "Both if possible. Otherwise original table S7"
3. **Rule MN, grid.** The original's one-factor neighbours of (32, 8) in its Fig. 6 grid, against
   the plan's grid, which includes (64, 8) and (32, 4).
   **Answer (verbatim, 2026-09-28):** "Original's neighbours (8)"

**How S1 applies the answers:**
- Answer 1 gives two pre-registered verdicts, each with Holm's correction across its three baselines: M-75 for teacher-forced baselines (the claim as the original makes it) and M-76 for autoregressive baselines (architecture with the training regime held fixed).
- Answer 2: Table S7 architectures govern both verdicts. The parameter-matched variants of PLAN S2b run only if S2b's timing probe projects every baseline run, both specs, within the 20 CPU-hour cap. If run, they are reported alongside and never govern.
- Answer 3 fixes the grid in M-74.
