# Reply to Dr Li — to send when the project lands

**Send when the paper, the checkpoints and the code are all public.** Not before: the ask is that
he circulate it, and circulating something half-finished spends goodwill you only get once.

## What his reply changed, so the letter is accurate

| his answer | effect |
|---|---|
| aleatoric "not used in downstream training… reported in Fig. 3 (right) as an analysis" | **confirms C-14 outright.** §4.1 now says the discard is intended design, not a slip |
| λ "applied to the standard deviation… as intended, in contrast to Eq. 4 being more of a high-level explanation" | **resolves C-15.** A notational gap in the paper, not an implementation error |
| `max_iterations: 500` is "a typo"; recollection is 5,000 | C-13's three-way disagreement is a two-way one |
| "the checkpoint was released after a few iterations of the repo than the setup I used for the submission" | **the important one.** §6 narrowed again — the released repo is not the training repo, so the extrapolation's assumptions about initialisation and learning rate may not hold |

§6 is no longer "the release is internally inconsistent". It is "the released artifacts do not
reproduce the checkpoint's variance state, and the author's account is that the released repository
is not the one that trained it" — a documentation gap, and far less pointed. Worth telling him,
because he handed you that.

## Draft

> **Subject:** Re: Question about the released pretrain_rnn_ens.pt training configuration (RWM)
>
> Dear Dr Li,
>
> Thank you for replying so quickly, and so openly — it changed three things in the report rather
> than one, and all three for the better.
>
> Your confirmation that the aleatoric term is not used downstream and is reported as analysis
> settled a question I had otherwise established only by tracing the code, and it let me describe
> that as intended design instead of leaving a reader to wonder. Your answer on λ and the standard
> deviation turned what I had written up as a paper-versus-code discrepancy into what it actually
> is, a notational simplification in the equation. And your point that the checkpoint was released
> a few repository iterations after the setup you trained with reframed the section on the
> iteration count entirely: it is now a documentation gap between a release and a run, not an
> inconsistency in the release, which is both more accurate and much less pointed.
>
> The work is now complete and public:
>
> - **Paper:** [link]
> - **Code and evidence:** [link] — including a findings ledger recording every claim with its
>   evidence and status, and the five claims of my own I had to withdraw along the way
> - **Checkpoints:** [link]
>
> Two things I would value, if you have the time.
>
> First, permission to quote your reply. The report cites it as personal communication in three
> places — the aleatoric design intent, the λ question, and the repository drift — because in each
> case your answer is the evidence. I have written those passages to represent your position
> fairly, and I would rather you saw them than took my word for it. If you would prefer any of the
> three paraphrased instead of quoted, or removed, say so and I will change it.
>
> Second, and this is the larger ask: if you think the work is worth other people's attention,
> I would be grateful if you shared it. I am working on this outside a group, which means the
> obvious failure mode is that something is wrong in a way that is only obvious to someone who
> works on offline model-based RL every day. Two specific places where I would most value that
> scrutiny:
>
> - **The calibration measurement.** I report that neither uncertainty output is usable as an
>   interval — the epistemic term is about 40× overconfident at a 368-step horizon — while also
>   reporting that it ranks which predictions will be worse very well, which supports the use your
>   paper actually makes of it. I have tried hard to keep those two statements distinct and not to
>   claim you assert something you do not. Someone who uses these penalties in practice would know
>   immediately if I have drawn that line in the wrong place.
> - **The n = 4 problem.** The held-out arena has four mutually non-overlapping 400-step
>   trajectories, and I lean on an exact sign test over ten episodes rather than the bootstrap
>   because of it. I would like to know whether that is the right call or whether I am
>   over-correcting.
>
> Any criticism is welcome, including that a finding does not hold up. Several of mine already
> did not, and saying so is part of what the report is for.
>
> Thank you again for releasing the code and the checkpoint, and for answering as directly as you
> did.
>
> With thanks,
> [name]

## Before you send

- Fill the three links. The letter is weaker without all three, which is the reason to wait.
- Decide on the quoting request. If you would rather not cite him at all, tell me and I will
  convert the three passages to unattributed statements of what the code does — they are weaker
  that way, since his confirmation is what makes them authoritative, but it is a legitimate choice.
- If he declines to be quoted, that is a same-day change on my side, not a rewrite.
