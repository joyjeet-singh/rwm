# Reply to Dr Li — regenerated 2026-08-23

**Status: ready to send.** The paper, the checkpoints and the code are all public, which was the
condition for sending it — the ask is that he circulate the work, and circulating something
half-finished spends goodwill you only get once.

Regenerated against the current artifacts. Every figure below is read from `results/`, not
retyped, and every one was checked to appear verbatim in the built `PAPER.md`.

## What changed since the last version of this draft

| then | now |
|---|---|
| 12 comparative claims verified | 21 across 8 kinds, self-test 20/20 |
| 27 files / 5,928 values reproduced | 29 / 6,073, 100.00% bitwise |
| no data-budget comparison | **7,991 transitions against 6,000,000** — 751x less data |
| every epistemic result on one released checkpoint | **3 ensemble-5 arms of our own**, and a pre-registered rule that **does not generalise** |

The last row is why this needed rewriting rather than updating. The letter now has to report a
result that went against us, and it should — it is the part he is most likely to find useful.

## Draft

> **Subject:** Re: Question about the released pretrain_rnn_ens.pt training configuration (RWM)
>
> Dear Dr Li,
>
> Thank you again for replying so quickly, and so openly. Your answers changed three things in the
> report rather than one, and all three for the better: the aleatoric term being reported rather
> than consumed, λ applying to the standard deviation as intended, and the checkpoint having been
> released a few repository iterations after the setup you trained with. That last point reframed
> an entire section from an apparent inconsistency into what it actually is — a documentation gap
> between a release and a run.
>
> The work is now complete and public:
>
> - **Paper (PDF):** https://github.com/joyjeet-singh/rwm/blob/main/PAPER.pdf
> - **Code, data and evidence:** https://github.com/joyjeet-singh/rwm
> - **Checkpoints and model card:** https://huggingface.co/Joyjeetsingh/rwm-reproduction
>
> The repository carries a findings ledger of 183 entries recording every claim with
> its evidence and status, including 6 numbered retractions of my own and
> 2 further ones that withdraw framings. Every number in the paper is
> generated from a file under `results/`; the build also verifies 21 *comparative* claims
> — that an interval does or does not overlap, that a named cell really is the extremum, that a
> stated change has the sign claimed — because a correct number in a wrong sentence is the failure
> mode a numeral check cannot see, and I shipped six of those in an earlier draft.
>
> **Three things I think are worth your time.**
>
> **1. Ensemble disagreement beats a free baseline, and I went in expecting the opposite.**
> The follow-up justifies disagreement as a trust metric because it closely follows the trend of
> the prediction error. I wanted to test that against the most trivial competitor I could think
> of: the forecast step index. Error grows with rollout depth, so a counter already tracks it and
> costs nothing. If a counter ranked error as well, the trust metric would be adding very little.
>
> It does not. On the scalar your code applies — `means.std(0).sum(-1)` at `envs/base.py:166` —
> against total absolute error over 20 non-overlapping 400-step trajectories,
> disagreement correlates +0.605 [+0.545, +0.694] against the counter's +0.269. A
> paired bootstrap on the difference excludes zero at 4 of
> 4 horizons. Holding forecast depth *exactly* constant — correlating within
> each step, so the index cannot contribute at all — still gives +0.739, positive at
> 368 of 368 steps. At a single step it reaches
> +0.994 [+0.918, +0.999], very nearly a perfect ranking of realised error.
>
> **2. I tried to replicate that on a model I trained, and my own pre-registered rule failed.**
> Every epistemic measurement above is on your released checkpoint, because my main arms run at
> ensemble size 1 where the epistemic term is identically zero. So I trained 3 Arm A
> arms at ensemble size 5 and committed a rule to git beforehand: the finding generalises if
> disagreement leads the index at every horizon *and* the paired difference excludes zero at a
> majority.
>
> It returned **does not generalise**. The first condition passed completely —
> 12 of 12 seed-horizon cells. The second failed:
> 1 of 4 horizons. My own arms have only 4
> independent trajectories in a genuinely held-out arena, and I wrote the rule without checking
> what it could detect there — at one horizon its power is about 24%. So the
> direction replicated and the separation did not, and I report the verdict the rule returned
> rather than the direction I would have preferred. Your claim is established on your checkpoint
> and supported but not established on mine.
>
> **3. A data-budget comparison, which is the one part of the sample-efficiency result I could
> measure.** Your Table I reports 6,000,000 state transitions of world-model pretraining. Mine
> consume **7,991** distinct transitions — 751x less, 0.133% of your
> budget — and still reproduce the autoregressive-versus-teacher-forcing result at
> 4.61x and still beat a hold-last floor by 2.8x at a 368-step horizon.
> That says nothing about policy transfer, and my evaluation distribution is narrower than yours
> in proportion, but it seemed worth putting a number to.
>
> The scale finding does stand: at the deployment horizon the epistemic term is
> 34.4x smaller than the realised error on your checkpoint, and
> 13.0x on mine, with 3.59% coverage at ±1σ where a calibrated
> Gaussian gives 68.3%. I have tried throughout to keep that separate from the ranking claim your
> paper actually makes. There is also a remedy: one multiplier per forecast horizon, fitted on one
> held-out episode and scored on the other, restores nominal coverage on 10 of
> 10 held-out cells where a single global multiplier manages
> 2.
>
> **Two things I would value, if you have the time.**
>
> First, permission to quote your reply. The report cites it as personal communication in three
> places — the aleatoric design intent, the λ question, and the repository drift — because in each
> case your answer is the evidence. I would rather you saw those passages than took my word that
> they represent you fairly. If you would prefer any paraphrased or removed, say so and I will
> change it that day.
>
> Second, the larger ask: if you think the work is worth other people's attention, I would be
> grateful if you shared it. I work on this outside a group, and the obvious failure mode is that
> something is wrong in a way that would be immediately obvious to someone who does offline
> model-based RL daily. Three places I would most value that scrutiny:
>
> - **Whether the ranking/scale line is drawn in the right place.** I claim the quantity is a
>   usable ranking signal and not a usable interval, and that your paper's use of it is the
>   former. Someone who applies these penalties in practice would know at once if that is wrong.
> - **The dependence correction.** Treating 45 state dimensions as independent
>   trials overstated my evidence by up to 10^13; permuting whole trajectories
>   is the right null as far as I can see, but it is the change that most altered my conclusions
>   and I would like it checked by someone who has not spent a month convincing themselves of it.
> - **The n = 4 problem**, which is what defeated the replication above. If there is a
>   better way to get power out of a ten-episode dataset than the one I used, I would like to know
>   it.
>
> Any criticism is welcome, including that a finding does not hold up. Several of mine already did
> not, and recording that is part of what the report is for.
>
> Thank you again for releasing the code and the checkpoint, and for answering as directly as you
> did.
>
> With thanks,
> [name]

## Before you send

- **Check the double-blind position.** The paper is being prepared for TMLR, whose submission is
  anonymous. The GitHub repository and the HuggingFace model are already public under your name
  and TMLR permits public preprints and code, so linking them is not a problem in itself — but you
  are choosing to tell an author of work under review who you are. Worth doing deliberately. The
  letter keeps if you would rather wait for a decision.
- **Decide on the quoting request.** If you would rather not cite him, tell me and I will convert
  the three passages to unattributed statements of what the code does. Weaker — his confirmation
  is what makes them authoritative — but legitimate, and a same-day change.
- **The figures are read from the artifacts**, not retyped. If you edit the letter, do not
  hand-edit a number: tell me and I will regenerate it.
