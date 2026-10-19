# Supplementary material

This document holds the text that left the paper's PDF to meet its length (ruling Y4): appendices, detail
tables and passages moved out of the main text whole. Nothing that left the PDF left the record. Every number below
is a placeholder (a key name in double braces) filled from `results/paper_numbers.json` by `scripts/build_paper.py`, exactly as the paper's
are, and the paper's checks read this file as they read the paper.

`docs/SUPPLEMENT.md` is generated from `docs/SUPPLEMENT.template.md`; edit the template, never the generated file.

## Contents

The sections are added as they leave the paper. Each keeps the heading it had in the paper and
says where in the paper it was.

## S1 What testing the untested claims would require

*Was the paper's Appendix C, "what testing the untested claims would require"; moved here to meet the length limit.*

Appendix D's first table marks {{orig_n_tested}} claims tested and the rest not. "Not tested" is an apology
unless it comes with a price, so here is what each would cost. We give compute orders where we
can estimate them honestly from this project's own measurements and say so where we cannot.

**Every row needs what this reproduction did not have: interaction.** Our arms train on the released CSV, which is a recording. Those claims need a
policy acting in an environment, simulated or real, and the environment responding. In
simulation that means Isaac Lab, which needs an RTX-class NVIDIA GPU, and no amount of CPU
substitutes: the reference's data generation is GPU-parallel simulation, not a data-loading
problem. For the hardware-transfer and real-robot rows the binding constraint is a robot rather
than compute. **A GPU would not be enough on its own.** The code that generates data is in
neither repository this reproduction pins: the only code that touches the file reads it
(`train.py:44` in the lite release), the lite release's environment rolls the learned model forward
rather than physics, and its readme places collection in a third repository, the authors' Isaac Lab
extension (`readme.md:13`), which this reproduction does not pin and which would need Isaac Lab and
an RTX-class GPU (ledger `D-36`).

| untested claim | what it needs | order |
|---|---|---|
| Sample efficiency, {{c2_ref}} against ~250M transitions (§IV-E) | Isaac Lab, an RTX-class GPU, the MBPO-PPO loop, and a PPO baseline run to convergence for the comparison | the reference reports {{c2_ref}} pretraining transitions and 50 min of RWM training on their hardware; the PPO baseline's 250M is the dominant cost |
| MBPO-PPO beats SHAC and Dreamer (§IV-E) | the above, plus SHAC and Dreamer implementations at matched budgets | three policy-learning stacks, each tuned enough that the comparison is fair — the largest engineering item here |
| Zero-shot hardware transfer (§IV-E) | all of the above, plus an ANYmal, a safe test area, and the sim-to-real stack | not estimable in compute; the binding constraint is hardware access, not GPU hours |
| Generality across quadruped, humanoid, manipulation (§IV-D) | recorded state-action data from a humanoid and a manipulator, which means Isaac Lab and a policy in each environment to generate it — the released CSV is one robot on one terrain | one data-generation run per morphology, plus a world-model training campaign each on the scale of ours, {{rt_runs}} runs in {{rt_hours}} h; the model training is the cheap half and the data is not |
| Offline MBRL on real robots (2504.16680v1) | a real robot, a logged dataset from it, and the offline MBRL loop | not estimable in compute; hardware access again, and a claim the follow-up itself states as prospective |
| Whether the penalty improves the learned policy (2504.16680v1 §5) | Isaac Lab, the MOPO-PPO loop, and at minimum an ablation with the penalty weight at zero | one policy-learning stack; the cheapest of the rows that need a simulator, and the one that would bound §11's open question about what the miscalibration costs |


**Two claims this table once priced as within reach of this setup have since been run**: the
configuration claim (§5.2) and the architecture claim (§5.3), {{rt_pre_runs}} runs and
{{rt_pre_hours}} h of CPU training between them (Appendix B). The {{appE_n_sim_word}} that remain all
need a simulator or hardware, and no amount of care with the released CSV changes that.

**What we would do first.** The penalty ablation. It is the cheapest of the simulator-requiring
items, it bears directly on a limitation §11 states our measurements cannot settle — whether the
miscalibration we document costs anything downstream, where §11's policy-free proxy tests only
whether the per-horizon correction reorders the penalty component and measures no cost — and it
needs no robot.



---
