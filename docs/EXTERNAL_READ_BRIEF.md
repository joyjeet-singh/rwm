# Brief for an external scientific read

**What is wanted:** two hours from one or two people who know model-based RL, reading for the
**argument** and not for consistency. Please do not check numbers. Twenty-three automated gates
already check that every sentence agrees with the artifact behind it, and they are good at it.
None of them can tell whether the artifacts answer the right question, and every issue worth
finding now is of that kind.

If you have time for only one thing, read §6.2 and §6.7 and press on the three questions below.

---

## One page on what the paper claims

We rebuilt the proprioceptive dynamics model of the Robotic World Model (arXiv:2501.10100) and its
uncertainty-aware follow-up (arXiv:2504.16680) from scratch on CPU, checked the rebuild against
the released implementation at gradient level, and then measured what the released checkpoint's
uncertainty outputs report.

**Four claims, in the order the paper makes them.**

1. **The base paper's training claim reproduces.** Autoregressive training beats teacher forcing
   on held-out episodes, by 4.61× on the reference's own relative-L1 error at h = 368, under a
   decision rule committed to git before the runs. The advantage grows monotonically with forecast
   horizon and the gap spans zero only at h = 1.

2. **Neither uncertainty output is usable as an interval.** At one step ahead the ensemble
   disagreement the method penalises rewards with is 8.3× smaller than realised error, with 16.22%
   of outcomes inside ±1σ against a calibrated 68.27%. It deteriorates with horizon from there.
   The per-member σ the method computes and discards is worse still, and §6.3 derives why: the
   implemented state loss puts a reparameterised *sample* into a squared error, whose optimum in σ
   is exactly zero. §6.3 demonstrates that against synthetic data with known noise.

3. **As a ranking it is much better.** Disagreement beats the forecast step index — a free counter
   neither paper ran — at every horizon, and still correlates +0.419 with realised error once both
   the rollout and the forecast depth are held constant. But that evidence is in-sample for a
   checkpoint trained on all ten episodes, and a pre-registered replication on models we trained
   returned DOES NOT GENERALISE.

4. **The interval is repairable, and one released defect is worth fixing today.** One multiplier
   per horizon, fitted on one held-out episode and scored on the other, restores nominal coverage
   on every held-out cell where a global multiplier does not. Separately, the released evaluation
   pairs each state with the previous step's action; scored causally the released checkpoint is
   75% better than its own harness reports.

**Scale, so you can calibrate how much to trust each.** Two CPU cores, 46.3 hours of training
across 26 runs, 0.133% of the reference's world-model data budget. The out-of-sample arena has
**four** mutually non-overlapping 400-step trajectories, and that bounds every long-horizon claim
in the paper.

---

## The three questions to press on

### 1. Is the calibration comparison the right comparison at all?

This is the objection we most expect and the one we have tried hardest to meet, so please attack
the meeting of it rather than the objection.

A predicted σ is **conditional**: given this input, how uncertain is the next state? In an
open-loop rollout the input is the model's own previous output, which is wrong by an amount σ
never claimed to describe. So comparing a per-step conditional σ against *accumulated* rollout
error is arguably comparing two different things, and the h = 368 figure could be an artifact of
that mismatch.

Our answer is to lead with **h = 1**, where nothing has accumulated and σ is asked exactly the
question it was trained on — and it is 8.3× out there. §6.2 states the objection and answers it in
two paragraphs.

**Press on:** is h = 1 actually clean? The model is trained on 8-step windows with the first 32
steps as history, so "one step ahead" still involves a recurrent state built from real data — is
there a sense in which even h = 1 is not the conditional quantity we claim it is? And is
"deterioration from an already-broken start" the right reading of the curve, or does the curve
have a shape that argues for something else?

### 2. Is the ranking result carrying more weight than its evidence?

§6.7 is the paper's best positive result, and the abstract now says both of its limits: the
evidence is in-sample for a checkpoint that trained on all ten episodes, and the pre-registered
replication on our own ensemble-5 arms returned DOES NOT GENERALISE (because its second condition
needs the paired difference to exclude zero at a majority of horizons, and at n_independent = 4 it
does so at one).

**Press on:** given those two facts, is "as a ranking it is far better" a claim the paper is
entitled to make at all? We think yes — six controls, including one that holds both the rollout
and the forecast depth constant — but a reader who discounts everything in-sample is left with a
failed replication, and we would like to know if that reading is the reasonable one.

### 3. Is §6.4 new, and does the paper now say so correctly?

§6.4 argues that five ensemble heads on one shared trunk cannot disagree about anything the trunk
does not already carry — 89.15% of each member's parameters are shared, along with one recurrent
state. §6.10 measures the cost: an independent five-model ensemble is 2.03× better calibrated.

The revision added the literature this belongs to (Lee 2015, Fort 2019, BatchEnsemble, MIMO) and
now says the *mechanism is known* and that what is ours is finding it in a released robotics
checkpoint that its authors deployed on hardware, with the sharing quantified and the cost
measured.

**Press on:** is that positioning honest, or is it still claiming too much? And is the contrast in
§6.10 clean? It confounds independence with **capacity** — 3.49× more state-pathway parameters —
which §11 concedes and which `M-49` is a pre-registered attempt to fix by matching capacity at
reduced width. Is capacity-matching the right control, or is there a better one?

---

## What would be most useful to hear back

In rough order:

1. Any of the three above where you think the paper's answer does not hold.
2. Anything in the abstract that you would read as a stronger claim than the body supports.
3. A section you would cut. The paper is long, roughly a fifth of it is about its own process, and
   we would rather hear "§8 is too long" from you than from a reviewer.
4. Anything that reads as defensive rather than careful. The paper retracts twelve of its own
   claims and says so repeatedly; we cannot tell any more whether that reads as rigour or as
   anxiety.

**What is not useful:** arithmetic, citation formatting, or anything of the form "this number
disagrees with that number". That is what the gates are for, and if one has slipped through, the
gates are what should be fixed.
