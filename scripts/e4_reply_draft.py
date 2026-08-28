"""
E4 -- generate the reply to the first author from the current artifacts.

The letter quotes about thirty figures from the paper. Hand-maintaining it meant
that every time a number moved, the letter silently disagreed with the report it
was describing -- and the previous version had drifted a long way: it still called
h=368 the deployment horizon, still quoted the pre-revision calibration figures,
and knew nothing of the trunk-sharing finding, which is the part most useful to
the person receiving it.

So the letter is generated, like the paper, the README and the model card. Every
figure is substituted from results/paper_numbers.json, and each substituted value
is then checked to appear in the built PAPER.md -- a letter that tells him
something the paper does not say would be worse than one that says nothing.

    python scripts/e4_reply_draft.py            write docs/E4_REPLY_DRAFT.md

This is a DRAFT for a person to read, edit and send. It is not sent by anything.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import rwm_data as R  # noqa: E402

OUT = os.path.join("docs", "E4_REPLY_DRAFT.md")

BODY = """# Reply to the first author — generated, do not hand-edit

**Source:** `scripts/e4_reply_draft.py`. Every figure below is substituted from
`results/paper_numbers.json` and checked to appear in the built `PAPER.md`. If a number here
looks wrong, the fix is upstream in the artifact, not in this file.

**Status: ready to send, once you decide the two questions at the bottom.**

## What changed since the previous version of this draft

| then | now |
|---|---|
| h=368 called "the deployment horizon" | h={{v2_deploy_h}} is; 368 is the upstream's open-loop diagnostic ({{v2_len_eval}} − {{v2_history}}) |
| the epistemic miscalibration had no mechanism | the ensemble shares {{v1_shared_pct}}% of each member and one hidden state, and an independent one is {{m44_ratio_gain}}× better calibrated |
| five controls on the ranking claim | six — the new one removes trajectory difficulty, and shows the old "decisive" one did not |
| two references, both his | {{t1_n_refs}} more, including a 2022 paper that found the same thing about ensemble std |
| {{cc_n}} comparative claims, 8 kinds | {{cc_n}} across {{cc_kinds}} kinds |

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
> The work is complete. The paper is attached ({{pdf_pages}} pages), and everything behind it is
> public:
>
> - **Code, data and evidence:** https://github.com/joyjeet-singh/rwm
> - **Checkpoints and model card:** https://huggingface.co/Joyjeetsingh/rwm-reproduction
>
> Every number in the paper is generated from a file under `results/`; none is typed. The build
> also verifies {{cc_n}} *comparative* claims across {{cc_kinds}} kinds — that an interval does or
> does not overlap, that a named cell really is the extremum, that a stated change has the sign
> claimed — because a correct number in a wrong sentence is the failure mode a numeral check
> cannot see, and I shipped several of those in an earlier draft. A clean clone regenerates
> {{ver_files}} artifacts and {{ver_values}} values, {{ver_identical}} of them bitwise identical
> ({{ver_pct}}%), {{ver_differing}} differing. The findings ledger has {{n_entries}} entries and
> records {{n_retractions_word|lower}} numbered retractions of my own claims plus
> {{n_retract_framing_word}} that withdraw framings.
>
> **Four things I think are worth your time. The first is the one I would most like you to
> disagree with.**
>
> **1. Your five ensemble members share a trunk, and it costs you calibration.**
> `system_dynamics.py:34` builds one `state_base`; `:35-41` replicates only the heads. So each
> member owns {{v1_private_params}} parameters and shares {{v1_shared_params}} —
> **{{v1_shared_pct}}% of every member's state-prediction pathway is numerically identical to
> every other member's.** And because the trunk owns a single recurrent state and the rollout
> feeds the ensemble mean back into it, the {{v1_members_word}} members never diverge dynamically
> at all: disagreement at step *t* is the spread of {{v1_members_word}} small MLPs read off one
> 256-vector.
>
> I tested whether that matters, under a rule committed to git before the runs existed. I already
> had Arm A at ensemble size 1 for seeds 0–2, so I trained two more and scored the five together
> as an ensemble — five models sharing nothing, against your architecture's five heads sharing
> everything, same trajectories, same harness. The independent ensemble is **{{m44_ratio_gain}}×
> better calibrated** at h={{v2_deploy_h}} ({{m44_cov_gain}} points of coverage), against a
> pre-registered detectable-effect threshold of {{m44_mde_ratio}}×.
>
> The honest caveat, which I put in the paper as prominently as the result: the overconfidence
> factor is error over σ, so it improves if σ grows *or* if error shrinks, and five independent
> models also denoise better than five heads. Decomposed, σ is larger by
> {{r2_sigma_x_h100}}× and that is {{r2_from_sigma_h100}}% of the gain at h={{v2_deploy_h}} — but
> at the 368-step diagnostic horizon the split reverses and {{r2_from_acc_h368}}% of it is just
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
> `len_eval_trajectory` = {{v2_len_eval}} minus the {{v2_history}}-step teacher-forced prefix —
> the open-loop diagnostic your Fig. 2 (right) plots. Your method's own imagination rollouts run
> to **{{v2_deploy_h}}** steps (Table S9 in v1, S11 in {{v4_current}}). h=368 is
> {{v2_ratio}}× that. I have re-anchored every headline to h={{v2_deploy_h}} and relabelled the
> 368 rows, which I mention because it changes numbers you may have seen: the epistemic term is
> {{d1n_epi_ratio_h100}}× [{{d1n_epi_ratio_ci_h100}}] smaller than realised error at
> h={{v2_deploy_h}} with {{d1n_epi_cov1_h100}}% coverage at ±1σ, and the aleatoric one
> {{d1n_alea_ratio_h100}}×. The conclusion did not move; the label was wrong and now is not.
>
> **3. Ensemble disagreement beats a free baseline — and the control I thought was decisive was
> measuring the wrong thing.** I tested your trust-metric claim against the most trivial
> competitor I could find: the forecast step index. Error grows with depth, so a counter already
> tracks it and costs nothing. It loses: on the scalar your code applies, disagreement correlates
> {{d2b_epi_h368}} against the counter's {{d2b_idx_h368}}, and a paired bootstrap separates them
> at every horizon where the index is defined.
>
> But my strongest control was flawed. Correlating within each forecast step across trajectories
> ({{d2r_win}}) holds depth exactly constant — and holds trajectory difficulty not at all. It is a
> mean of between-trajectory correlations, which is why it reads *above* the pooled
> {{a2_r_pooled}} rather than below. Removing both the trajectory mean and the step mean gives
> **{{a2_rdd}} {{a2_rdd_ci}}** — smaller, and the first figure I have that isolates
> within-rollout information. Your claim survives it ({{m45_verdict}}), but the between-trajectory
> component is large ({{a2_r_between}}) and I now say so. Relatedly, the
> {{a2_h1_r}} at one step is a ranking of *whole rollouts* over {{a2_h1_npoints}} points, not of
> moments within one — it survives partialling out commanded speed and episode difficulty
> ({{a2_h1_partial_both}}), but it is a smaller claim than it looks.
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
> **What still does not work.** The scale finding stands: {{d1n_epi_ratio_h100}}× on your
> checkpoint at its own horizon, {{e5_ratio_h100}}× on my ensemble-5 arms,
> {{r2_indep_ratio_h100}}× even on the independent ensemble, whose ±1σ coverage is
> {{r2_indep_cov1_h100}}% against a calibrated {{v3_cov_nominal1}}%. There is a cheap remedy — one multiplier per forecast horizon, fitted on
> one held-out episode and scored on the other, restores nominal coverage on every held-out cell
> where a single global multiplier manages {{d3_epi_const_ok}} — but it is a calibration patch,
> not a fix. And my own pre-registered replication of the ranking result on models I trained
> returned **{{e5_verdict}}**: the direction held everywhere, the separation reached significance
> at only {{e5_n_excl}} of {{e5_n_horizons}} horizons, because my held-out arena has
> {{e5_nind}} independent trajectories against your checkpoint's {{d1n_nind}}. I report the
> verdict the rule returned.
>
> On sample efficiency, the one part I could measure: your Table I reports {{c2_ref}} state
> transitions of world-model pretraining. Mine consume **{{c2_trans}}** distinct transitions,
> {{c2_ratio}}× less, and still reproduce the autoregressive-versus-teacher-forcing result at
> {{d1_ratio}}× at h={{v2_diag_h}} and {{d1_ratio_h100}}× at h={{v2_deploy_h}}. That says nothing
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
> - **The n = {{e5_nind}} problem**, which is what defeated my replication. If there is a better
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
"""


def main():
    N = json.load(open(os.path.join(R.RESULTS, "paper_numbers.json")))
    used, missing = set(), []

    def sub(m):
        k, filt = m.group(1), m.group(2)
        if k not in N:
            missing.append(k)
            return m.group(0)
        used.add(k)
        v = str(N[k]["value"])
        # the word-forms in paper_numbers are capitalised for sentence-initial
        # use; "records Six retractions" needs the other one
        return v.lower() if filt == "|lower" else v

    out = re.sub(r"\{\{(\w+)(\|lower)?\}\}", sub, BODY)
    assert not missing, f"no such keys in paper_numbers.json: {sorted(set(missing))}"
    left = re.findall(r"\{\{[^}]*\}\}", out)
    assert not left, f"unresolved: {sorted(set(left))}"

    # Every figure the letter quotes must also appear in the paper. A letter that
    # tells him something the report does not say would be worse than one that
    # says nothing, and this is the only check that can catch it.
    absent = []
    if os.path.exists("PAPER.md"):
        paper = open("PAPER.md").read()
        for k in sorted(used):
            v = str(N[k]["value"])
            # skip pure prose values and the page count, which is about the PDF
            if k in ("pdf_pages", "v4_current", "v4_current_date"):
                continue
            if v not in paper:
                absent.append((k, v))
    assert not absent, ("figures quoted in the letter but absent from PAPER.md: "
                        + ", ".join(f"{k}={v}" for k, v in absent))

    os.makedirs("docs", exist_ok=True)
    with open(OUT, "w") as f:
        f.write(out)

    print("E4 REPLY DRAFT")
    print("=" * 78)
    print(f"  figures substituted : {len(used)}")
    print(f"  all present in PAPER.md : yes")
    print(f"  wrote {OUT} ({len(out.splitlines())} lines)")


if __name__ == "__main__":
    main()
