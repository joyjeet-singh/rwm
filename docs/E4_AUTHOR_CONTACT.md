# E4 — contacting the authors: what to send, and why it matters

**This is yours to send. I have not contacted anyone.**

## Why it is worth doing before submission

§6 of the paper says the released checkpoint's variance state is unreachable at any of the three
iteration counts its own artifacts give — config 500, paper 2,500, checkpoint tag 5,000 — because
a constant-rate fit implies ~153,000.

E5's assumption table shows **two things we cannot rule out** that would explain the whole gap
with no inconsistency at all:

- a **warm start** from an earlier checkpoint, which makes the implied count a lower bound on
  total optimisation rather than an estimate of one run, and
- a **different initialisation of `log_delta_logstd`**, which rescales the implied count linearly.

Neither is visible from the released files. One sentence from the authors likely settles §6
outright — in either direction. A reviewer will ask whether they were asked, and "contacted on
[date], no response" is a materially stronger position than silence.

## Draft — adjust the tone as you like

> **Subject:** Question about the released `pretrain_rnn_ens.pt` training configuration (RWM)
>
> Dear Dr Li, Prof. Krause and Prof. Hutter,
>
> I have been working through an independent reproduction of the proprioceptive dynamics model
> from *Robotic World Model* (arXiv:2501.10100) and the uncertainty-aware follow-up
> (arXiv:2504.16680), rebuilding the model from scratch and checking it against
> `robotic_world_model_lite` at `13a798e9` and `rsl_rl_rwm` at `18eebcdd`. It reproduces the
> autoregressive-versus-teacher-forcing result clearly, and I am preparing a reproduction report.
>
> One question I cannot answer from the released artifacts, and I would rather ask than speculate
> in print.
>
> In `pretrain_rnn_ens.pt` the state heads' `log_delta_logstd` has moved a long way from its
> initialisation — mean about −14.46, against −1e-4 at init. Fitting the rate at which that
> parameter moves across my own runs at the configured learning rate of 1e-4, and extrapolating,
> implies on the order of 1.5×10⁵ optimisation steps. The released config sets
> `max_iterations: 500`, the paper describes 2,500, and the checkpoint is tagged 5,000.
>
> The most likely explanations I can see are that the released checkpoint was warm-started from
> an earlier run, or that `log_delta_logstd` was initialised differently from the released
> default, or that a learning-rate schedule was used. Any of these would account for it
> completely, and I would like to describe it correctly rather than present the arithmetic as a
> puzzle.
>
> Could you say which, if any, applies? I am equally glad to be told the extrapolation is wrong.
>
> Two smaller points, in case they are useful:
>
> - Eq. 4 of the follow-up defines the penalty on the **variance** across ensemble members, while
>   `rsl_rl/modules/system_dynamics.py:126` computes `state_means.std(dim=0)` — a standard
>   deviation. With λ = 1 the two differ by a square. Is the code or the equation the intended
>   form?
> - In `robotic_world_model_lite/scripts/envs/base.py:142` the aleatoric term returned by
>   `system_dynamics.forward` is bound to a local that is not read again, so only the epistemic
>   term reaches the reward penalty. Is the aleatoric head intended to be used downstream, or is
>   it there to shape training only?
>
> The reproduction, including everything above with file and line references, is available if it
> would be useful. Thank you for releasing the code and the checkpoint — the work would not have
> been possible otherwise.
>
> With thanks,
> [name]

## After you send it

Tell me the date and I will put it in the paper. The sentence is already drafted at the end of §6
and currently reads that no contact has been made; it becomes "contacted on [date]; no response as
of submission" or records their answer.

If they confirm a warm start or a different initialisation, **§6 changes substantially** — the
finding becomes a documentation gap rather than an inconsistency, and the section should shrink to
a paragraph. That is a good outcome and worth having before a reviewer raises it.
