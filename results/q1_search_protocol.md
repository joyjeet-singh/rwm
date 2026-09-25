# A2 — survey protocol, fixed before anything was looked at

Written 2026-09-20 as step 1 of block A2, BEFORE any search was run and before any repository
was opened. It is not changed afterwards. A survey whose criteria move while it runs measures
the surveyor. Its sha256 is recorded in STATE.json and in the end-of-block report; if the file
and that hash disagree, the survey is void.

## 0. The question

Referee Q1 asks how far §6.3's σ = 0 result reaches. §2 of the paper states, explicitly as an
UNTESTED hypothesis, that any descendant of the PETS parameterisation which replaced the
likelihood with a sampled squared error inherits the same optimum. This block counts. It measures
nothing and trains nothing.

## 1. The construction being searched for

Two lines, from PETS (Chua, Calandra, McAllister, Levine, NeurIPS 2018) Appendix A.1:

    logvar = max_logvar - softplus(max_logvar - logvar)
    logvar = min_logvar + softplus(logvar - min_logvar)

The reference implementation this paper reproduces carries them in log-standard-deviation form at
`rsl_rl_rwm/rsl_rl/modules/architectures/mlp.py:92-93`. **Either form counts** — log-variance or
log-standard-deviation — and so does either naming convention (`logvar`/`log_var`/`logstd`/
`log_std`, `max_logvar`/`max_log_var`/`max_logstd`). What is required is the double-softplus
soft-clamp shape: an upper bound applied as `bound - softplus(bound - x)` and a lower bound
applied as `bound + softplus(x - bound)`, with the bounds being learnable parameters.

### Exact strings searched for

  S1  `max_logvar - softplus`
  S2  `min_logvar + softplus`
  S3  `max_logstd - softplus`
  S4  `min_logstd + softplus`
  S5  `max_logvar` together with `softplus` in one file
  S6  `logvar = self.max_logvar`
  S7  `soft_clamp` together with `logvar`

Whitespace and the `nn.functional.`/`F.` prefix are not significant and variants with either are
treated as the same string.

### Where searched

  W1  GitHub code search, via the web interface and via web search engines, for S1-S7.
  W2  The repositories that PETS itself names as its lineage, and repositories that name PETS,
      MBPO, PETS-style probabilistic ensembles or `rsl_rl` in their own README.
  W3  Forks and descendants of the two upstreams this paper pins, where they are distinct
      codebases rather than unmodified copies.

Search engines rank and truncate, and GitHub code search requires authentication for some
queries. **Whatever is found is a sample of convenience, not a census**, and §4 governs how the
result may be stated.

## 2. The inclusion test — two parts, and a repository needs both

A repository counts as INHERITS only if:

  (a) it carries the bounded-log-σ construction of §1, **and**
  (b) it trains that head against a squared error on a SAMPLED prediction — a reparameterised
      draw `mu + sigma * eps` scored by MSE or L2 — rather than against a likelihood.

**Part (b) is the one that matters and is the one that takes reading.** Part (a) is a text match;
part (b) requires opening the loss and reading what it does with the head's output.

A repository carrying the construction with a proper Gaussian negative-log-likelihood — a
`gaussian_nll`, a `-log p`, a `0.5*(logvar + (y-mu)^2/var)` or `torch.distributions` log_prob —
does **NOT** inherit the optimum, because the log-σ term opposes σ → 0. Such a repository is
counted separately as DOES NOT INHERIT. **It is not dropped from the count.**

## 3. The record — every repository examined, whatever the verdict

For each: the URL; the commit hash actually read; the file and line of the construction; the file
and line of the loss; and one verdict from exactly three:

  INHERITS              (a) and (b) both confirmed by reading
  DOES NOT INHERIT      (a) confirmed, (b) confirmed ABSENT — the loss is a likelihood
  COULD NOT DETERMINE   (a) confirmed, (b) not resolvable from the source available

**COULD NOT DETERMINE is a legitimate verdict and is never quietly converted into either of the
others.** A repository whose loss could not be located, or which offers both a likelihood and a
sampled-squared-error branch without the source showing which is used, is recorded as such.

A repository where (a) is absent is not "examined" for this count: it is out of scope, since the
question is about descendants of this construction.

## 4. How the result may be stated

As a count over what was examined, in this form and never another:

  "Of N repositories examined on <date> under the protocol in <file>, K carry the construction
   and J of those train it against a sampled squared error."

**Never as a count over a population.** No claim is made about how many such repositories exist,
what fraction of the field they are, or what the field does in general. The searching was ranked
and truncated by engines this block does not control.

## 5. The cap, and the stop rules

  - At most **25** repositories examined. Stop at 25 or at the budget, whichever comes first, and
    report how many were examined.
  - Budget 2.5 hours, hard stop at 3 hours whatever the state.
  - **If the count is low or zero, that is the finding.** It would mean the σ = 0 result is
    narrower than §2 currently implies and §2 would have to say so. Report it plainly.
    **Do not widen the search to find a better number.** The protocol is fixed here for exactly
    that reason.
  - If the network is unavailable, stop. This block cannot be done offline.
  - If the inclusion test turns out to be undecidable for most repositories, report that —
    "the question cannot be answered cheaply from source" is itself worth a sentence in §11.

## 6. What this block does not do

It does not clone, run, train, benchmark or modify any surveyed repository. It reads source. It
writes nothing to any repository it examines.
