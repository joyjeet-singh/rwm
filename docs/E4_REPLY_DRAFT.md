# Reply to Dr Li — to send now that the project has landed

**Status: ready to send.** The paper, the checkpoints and the code are all public, which was the
condition for sending it — the ask is that he circulate the work, and circulating something
half-finished spends goodwill you only get once.

Regenerated after Parts B–F. The earlier version of this draft quoted figures that have since
changed, and described the ordering finding in a way that is no longer accurate.

## What changed since the first draft, and why the letter had to change with it

| then | now |
|---|---|
| "the epistemic term is about 40× overconfident" | **34.4×**, measured at n_independent = 20 rather than 4 |
| "it ranks which predictions will be worse very well" | true of the **scalar** the method applies, and now tested against a baseline. **Not** true of the per-dimension sign counts, which no longer survive multiplicity correction |
| "five claims of my own I had to withdraw" | 6 numbered claims plus 2 framings |
| no baseline for the trust metric | there is one now, and **his claim wins it** |

The last row is the reason this letter is worth sending rather than just filing. The first draft
asked him to circulate a report that was, on balance, critical of his uncertainty work. This one
can tell him that the central use his paper makes of that quantity **survives an adversarial test
neither paper ran** — and that the part of the criticism that weakened is the part that was ours.

## Draft

> **Subject:** Re: Question about the released pretrain_rnn_ens.pt training configuration (RWM)
>
> Dear Dr Li,
>
> Thank you again for replying so quickly, and so openly. Your answers changed three things in the
> report rather than one, and all three for the better.
>
> Your confirmation that the aleatoric term is not used downstream and is reported as analysis
> settled a question I had otherwise established only by tracing the code, and let me describe it
> as intended design rather than leave a reader to wonder. Your answer on λ and the standard
> deviation turned what I had written up as a paper-versus-code discrepancy into what it actually
> is — a notational simplification in the equation. And your point that the checkpoint was
> released a few repository iterations after the setup you trained with reframed the section on
> the iteration count entirely: it is now a documentation gap between a release and a run, not an
> inconsistency in the release. That is both more accurate and much less pointed, and I would not
> have got there without you.
>
> The work is now complete and public:
>
> - **Paper (PDF):** https://github.com/joyjeet-singh/rwm/blob/main/PAPER.pdf
> - **Code, data and evidence:** https://github.com/joyjeet-singh/rwm
> - **Checkpoints and model card:** https://huggingface.co/Joyjeetsingh/rwm-reproduction
>
> The repository includes a findings ledger of 179 entries recording every claim with
> its evidence and status, including the six numbered claims of my own I had
> to withdraw and two further framings. Every number in the paper is generated
> from a file under `results/`; none is typed by hand.
>
> **One result I think will interest you, because it runs in your favour.**
>
> The follow-up justifies ensemble disagreement as a trust metric on the grounds that it closely
> follows the trend of the prediction error. I wanted to test that against the most trivial
> competitor I could think of — the forecast step index. Error grows with rollout depth, so a
> counter already tracks it, needs no ensemble and no second forward pass. If a counter ranked
> error as well, the trust metric would be adding very little.
>
> It does not. On the scalar your code actually applies — `means.std(0).sum(-1)` at
> `envs/base.py:166` — against total absolute error, over 20 non-overlapping 400-step
> trajectories: disagreement correlates +0.605 [+0.545, +0.694], the counter +0.269 [+0.106, +0.431].
> Partialling the counter out of both leaves disagreement essentially unchanged, and holding
> forecast depth *exactly* constant — correlating within each forecast step, so the index cannot
> contribute at all — still gives +0.739, positive at 368 of
> 368 steps. It is carrying real information about the individual rollout, not
> re-encoding the clock.
>
> I went in expecting the opposite. It is the one claim of either paper that this reproduction
> **strengthens** rather than qualifies.
>
> **And one where I had to correct myself, which bears on how the rest should be read.**
>
> An earlier draft converted per-dimension sign counts — "45 of 45 state dimensions positively
> correlated" — into P-values against a fair-coin null. That was wrong: the 45 dimensions are
> physically coupled, and error and σ share a forecast-depth trend, so a σ that grows with depth
> correlates with *any* trajectory's error. Permuting whole trajectories instead moves those
> P-values by up to a factor of about 10^13, and no such count in the paper survives a
> multiplicity correction. The direction of every count is unchanged; what is withdrawn is the
> strength of evidence I claimed for it. I mention it because it was the strongest-looking
> evidence in my draft and it was mine, not yours.
>
> The scale finding does stand: at the deployment horizon the epistemic term is
> 34.4× smaller than the realised error, with 3.59%
> coverage at ±1σ where a calibrated Gaussian gives 68.3%. I have tried hard throughout to keep
> that separate from the ranking claim your paper actually makes, and not to attribute to you a
> calibration claim you never made. There is also a remedy: one multiplier per forecast horizon,
> fitted on one held-out episode and scored on the other, restores nominal coverage on
> 10 of 10 held-out cells, where a single global multiplier manages
> 2 of 10.
>
> **Two things I would value, if you have the time.**
>
> First, permission to quote your reply. The report cites it as personal communication in three
> places — the aleatoric design intent, the λ question, and the repository drift — because in each
> case your answer is the evidence. I have written those passages to represent your position
> fairly, and I would rather you saw them than took my word for it. If you would prefer any of the
> three paraphrased rather than quoted, or removed, say so and I will change it that day.
>
> Second, and this is the larger ask: if you think the work is worth other people's attention, I
> would be grateful if you shared it. I am working on this outside a group, and the obvious
> failure mode is that something is wrong in a way that would be immediately obvious to someone
> who works on offline model-based RL every day. Three places where I would most value that
> scrutiny:
>
> - **Whether I have drawn the ranking/scale line in the right place.** I claim the quantity is a
>   usable ranking signal and not a usable interval, and that your paper's use of it is the former.
>   Someone who applies these penalties in practice would know at once if that distinction is
>   wrong, or if the ranking is doing less work than I credit it with.
> - **The dependence correction.** Permuting whole trajectories is the right null as far as I can
>   see, but it is the change that most altered the paper's conclusions, and I would like it
>   checked by someone who has not spent a month convincing themselves of it.
> - **The n = 4 problem.** The held-out arena has four mutually non-overlapping
>   400-step trajectories. I lean on an exact sign test over ten paired episodes
>   (all 10 favour autoregressive training, p = 0.0020) rather than the bootstrap
>   because of it. I would like to know whether that is the right call or whether I am
>   over-correcting.
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
  anonymous. The GitHub repository and the HuggingFace model are already public under your name,
  and TMLR permits public preprints and code, so linking them is not itself a problem — but you
  are choosing to tell an author of the work under review who you are, and that is worth doing
  deliberately rather than by default. If you would rather wait until after a decision, the letter
  keeps.
- **Decide on the quoting request.** If you would rather not cite him at all, tell me and I will
  convert the three passages to unattributed statements of what the code does. They are weaker
  that way — his confirmation is what makes them authoritative — but it is a legitimate choice,
  and it is a same-day change on my side.
- **The figures above are read from the artifacts**, not retyped, so they match the paper as
  built. If you edit the letter, do not hand-edit a number: tell me and I will regenerate it.
