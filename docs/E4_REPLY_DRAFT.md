# Reply to the first author — generated, do not hand-edit

**Source:** `scripts/e4_reply_draft.py`. Every figure below is substituted from
`results/paper_numbers.json` and checked to appear in the built `PAPER.md`. If a number here
looks wrong, the fix is upstream in the artifact, not in this file.

**Status: ready to send, once you decide the two questions at the bottom.**

## What changed since the previous version of this draft

| then | now |
|---|---|
| h=368 called "the deployment horizon" | h=100 is; 368 is the upstream's open-loop diagnostic (400 − 32) |
| the epistemic miscalibration had no mechanism | the ensemble shares 89.15% of each member and one hidden state, and an independent one is 2.03× better calibrated |
| five controls on the ranking claim | six — the new one removes trajectory difficulty, and shows the old "decisive" one did not |
| two references, both his | 10 more, including a 2022 paper that found the same thing about ensemble std |
| 46 comparative claims, 8 kinds | 46 across 19 kinds |

The trunk-sharing result is the reason this needed rewriting rather than updating. It is the one
finding in the report that is an actionable suggestion about his code rather than an observation
about it.

## Draft

> **Subject:** Re: Question about the released pretrain_rnn_ens.pt training configuration (RWM)
>
> Dear Dr Li,
>
> Thank you again for replying so quickly, and so openly. Your answers changed three things in
> the report rather than one, and all three for the better: the aleatoric term being reported
> rather than consumed, λ applying to the standard deviation as intended, and the checkpoint
> having been released a few repository iterations after the setup you trained with. That last
> point reframed an entire section from an apparent inconsistency into what it actually is — a
> documentation gap between a release and a run. The section now says so in those terms.
>
> The work is complete. The paper is attached (32 pages), and everything behind it is
> public:
>
> - **Code, data and evidence:** https://github.com/joyjeet-singh/rwm
> - **Checkpoints and model card:** https://huggingface.co/Joyjeetsingh/rwm-reproduction
>
> Every number in the paper is generated from a file under `results/`; none is typed. The build
> also verifies 46 *comparative* claims across 19 kinds — that an interval does or
> does not overlap, that a named cell really is the extremum, that a stated change has the sign
> claimed — because a correct number in a wrong sentence is the failure mode a numeral check
> cannot see, and I shipped several of those in an earlier draft. A clean clone regenerates
> 34 artifacts and 6,680 values, 6,680 of them bitwise identical
> (100.00%), 0 differing. The findings ledger has 200 entries and
> records six numbered retractions of my own claims plus
> six that withdraw framings.
>
> **Four things I think are worth your time. The first is the one I would most like you to
> disagree with.**
>
> **1. Your five ensemble members share a trunk, and it costs you calibration.**
> `system_dynamics.py:34` builds one `state_base`; `:35-41` replicates only the heads. So each
> member owns 77,492 parameters and shares 636,672 —
> **89.15% of every member's state-prediction pathway is numerically identical to
> every other member's.** And because the trunk owns a single recurrent state and the rollout
> feeds the ensemble mean back into it, the five members never diverge dynamically
> at all: disagreement at step *t* is the spread of five small MLPs read off one
> 256-vector.
>
> I tested whether that matters, under a rule committed to git before the runs existed. I already
> had Arm A at ensemble size 1 for seeds 0–2, so I trained two more and scored the five together
> as an ensemble — five models sharing nothing, against your architecture's five heads sharing
> everything, same trajectories, same harness. The independent ensemble is **2.03×
> better calibrated** at h=100 (+7.12 points of coverage), against a
> pre-registered detectable-effect threshold of 1.45×.
>
> The honest caveat, which I put in the paper as prominently as the result: the overconfidence
> factor is error over σ, so it improves if σ grows *or* if error shrinks, and five independent
> models also denoise better than five heads. Decomposed, σ is larger by
> 1.65× and that is 71% of the gain at h=100 — but
> at the 368-step diagnostic horizon the split reverses and 57% of it is just
> the better prediction. And independently-seeded runs differ in initialisation *and* data
> ordering, so this bounds the architectural effect rather than isolating it.
>
> Still: if the intent is a deep ensemble in the Lakshminarayanan sense, five heads on a shared
> trunk is not one, and the spread it produces is a lower bound on epistemic uncertainty by
> construction. Replicating the trunk is the obvious change and it is not expensive at this model
> size. That is the one concrete suggestion I have about your code.
>
> **2. I had your deployment horizon wrong, and fixing it is a correction to me, not to you.**
> Earlier drafts of mine called h=368 "the deployment horizon". It is not: it is
> `len_eval_trajectory` = 400 minus the 32-step teacher-forced prefix —
> the open-loop diagnostic your Fig. 2 (right) plots. Your method's own imagination rollouts run
> to **100** steps (Table S9 in v1, S11 in v3). h=368 is
> 3.68× that. I have re-anchored every headline to h=100 and relabelled the
> 368 rows, which I mention because it changes numbers you may have seen: the epistemic term is
> 33.4× [28.7, 39.0] smaller than realised error at
> h=100 with 4.61% coverage at ±1σ, and the aleatoric one
> 11,683×. The conclusion did not move; the label was wrong and now is not.
>
> **3. Ensemble disagreement beats a free baseline — and the control I thought was decisive was
> measuring the wrong thing.** I tested your trust-metric claim against the most trivial
> competitor I could find: the forecast step index. Error grows with depth, so a counter already
> tracks it and costs nothing. It loses: on the scalar your code applies, disagreement correlates
> +0.605 against the counter's +0.269, and a paired bootstrap separates them
> at every horizon where the index is defined.
>
> But my strongest control was flawed. Correlating within each forecast step across trajectories
> (+0.739) holds depth exactly constant — and holds trajectory difficulty not at all. It is a
> mean of between-trajectory correlations, which is why it reads *above* the pooled
> +0.605 rather than below. Removing both the trajectory mean and the step mean gives
> **+0.419 [+0.318, +0.576]** — smaller, and the first figure I have that isolates
> within-rollout information. Your claim survives it (SUPPORTED), but the between-trajectory
> component is large (+0.878) and I now say so. Relatedly, the
> +0.994 at one step is a ranking of *whole rollouts* over 20 points, not of
> moments within one — it survives partialling out commanded speed and episode difficulty
> (+0.995), but it is a smaller claim than it looks.
>
> **4. Two pieces of context you may already know, and one you may not.** Lu et al. (ICLR 2022,
> arXiv:2110.04135) compared uncertainty heuristics in offline MBRL and reported rank and
> bivariate correlation separately — the ranking-versus-scale distinction, four years earlier. It
> supports you: they found the ensemble standard deviation, the exact quantity your code applies,
> to correlate with model error better than MOPO's or MOReL's penalties.
>
> The one you may not: the bounded log-σ head is inherited line for line from PETS
> (`architectures/mlp.py:92-93` against PETS Appendix A.1), but PETS pairs it with a Gaussian
> NLL, and `system_dynamics.py:283` substitutes squared error on a reparameterised sample. The
> log-σ term is what opposes σ → 0; without it the optimum is σ = 0 exactly. So the aleatoric
> collapse follows from the *substitution*, not the parameterisation — which means any descendant
> of that lineage making the same swap inherits it. I flag that as an untested hypothesis; I have
> not looked at any other repository.
>
> **What still does not work.** The scale finding stands: 33.4× on your
> checkpoint at its own horizon, 10.5× on my ensemble-5 arms,
> 5.2× even on the independent ensemble, whose ±1σ coverage is
> 15.31% against a calibrated 68.27%. There is a cheap remedy — one multiplier per forecast horizon, fitted on
> one held-out episode and scored on the other, restores nominal coverage on every held-out cell
> where a single global multiplier manages 2 — but it is a calibration patch,
> not a fix. And my own pre-registered replication of the ranking result on models I trained
> returned **DOES NOT GENERALISE**: the direction held everywhere, the separation reached significance
> at only 1 of 4 horizons, because my held-out arena has
> 4 independent trajectories against your checkpoint's 20. I report the
> verdict the rule returned.
>
> On sample efficiency, the one part I could measure: your Table I reports 6,000,000 state
> transitions of world-model pretraining. Mine consume **7,991** distinct transitions,
> 751× less, and still reproduce the autoregressive-versus-teacher-forcing result at
> 4.61× at h=368 and 2.58× at h=100. That says nothing
> about policy transfer, and my evaluation distribution is narrower in proportion.
>
> **Two things I would value, if you have the time.**
>
> First, **permission to quote your reply.** The paper cites it as personal communication in three
> places — the aleatoric design intent, the λ question, and the repository drift — because in each
> case your answer is the evidence rather than a decoration on it. The full exchange is included
> as an anonymised supplementary file so a reviewer can check the quotations rather than take my
> word for them. I would rather you read those passages than trust me that they represent you
> fairly. If you would prefer any of them paraphrased or removed, say so and I will change it
> that day; the findings do not depend on them.
>
> Second, the larger ask: **if you think the work is worth other people's attention, I would be
> grateful if you shared it.** I work on this outside a group, and the obvious failure mode is
> that something is wrong in a way that would be immediately obvious to someone who does offline
> model-based RL daily. Three places I would most value that scrutiny:
>
> - **The trunk-sharing claim.** It is the strongest suggestion I make about your code and the one
>   I am least certain of. If there is a reason to share the trunk that I have not understood —
>   memory, stability, something about the recurrent state — I would rather hear it than publish
>   the recommendation.
> - **Whether the ranking/scale line is drawn in the right place.** I claim the quantity is a
>   usable ranking signal and not a usable interval, and that your paper's use of it is the
>   former. Someone who applies these penalties would know at once if that is wrong.
> - **The n = 4 problem**, which is what defeated my replication. If there is a better
>   way to get power out of a ten-episode dataset than the one I used, I would like to know it.
>
> Any criticism is welcome, including that a finding does not hold up. Several of mine already did
> not, and recording that is part of what the report is for.
>
> Thank you again for releasing the code and the checkpoint, and for answering as directly as you
> did. The reproduction would not have been possible otherwise, and the parts of it that
> strengthen your claims are as much a result of that openness as the parts that qualify them.
>
> With thanks,
> [name]

## Before you send

- **Attach the paper.** The build is anonymised for TMLR submission and carries no author name, so
  either rebuild it non-anonymised or say who you are in the message. The letter says "attached"
  rather than linking to `PAPER.pdf` in the repository so he can forward it to colleagues without
  them needing the repo.
- **You are choosing to break your own anonymity**, deliberately. The repository and the
  HuggingFace model are already public under your name and TMLR permits public code and preprints,
  so this is allowed — but it tells an author of work under review who you are. The letter keeps if
  you would rather wait for a decision.
- **Declare the conflict to the Action Editor** either way, once you submit. He now knows the paper
  exists; none of the three authors should be assigned to review it, and OpenReview's automatic
  conflict detection cannot see a private email.
- **If he declines the quoting request**, tell me and I will convert the three passages to
  unattributed statements of what the code does, and set the consent line in the supplementary
  transcript accordingly. Weaker — his confirmation is what makes them authoritative — but
  legitimate, and a same-day change.
- **Do not hand-edit a number in this letter.** It is generated; fix the artifact and re-run
  `scripts/e4_reply_draft.py`.
