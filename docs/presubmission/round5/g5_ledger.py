"""G5 items 1-3: the readings into the record (PLAN round 5, G5).

Appends S-22 (withdraws M-65's reading; evidence class), S-23 and S-24 (framings withdrawn), C-17 (corrects C-09; Table S8),
C-18 (per-head resampling: online path yes, offline path no) and R-89 (corrects R-75's survey count wording); sets M-65's and
M-96's Status lines (the sanctioned in-place edits for claims an S- entry withdraws); and moves RESULTS.md's rows and its C-
example. Every figure is formatted from an artifact; the claims each entry makes about an artifact are asserted first.
Writes .bak copies outside the repository; refuses to run twice. From the repository root:
    $PY docs/presubmission/round5/g5_ledger.py
"""
import json
import os
import re
import shutil

L, RES = "FINDINGS_LEDGER.md", "RESULTS.md"
EV = "/Users/Shared/rwm_verify/evidence/R5G5"
J = lambda p: json.load(open(p))
led = open(L, encoding="utf-8").read()
res = open(RES, encoding="utf-8").read()
nxt = lambda pfx: max(int(n) for n in re.findall(rf"^### {pfx}-(\d+) ", led, re.M)) + 1
assert (nxt("S"), nxt("C"), nxt("R")) == (22, 17, 89), (nxt("S"), nxt("C"), nxt("R"))
assert "### S-22 " not in led

# ------------------------------------------------------------------ the evidence
n8 = J("results/n8_tails.json"); m65 = J("results/m65_gaussian_nominal.json")
cells = [r for c in n8["cells"].values() for r in c["by_horizon"].values()]
over = [r for r in cells if r["m65_verdict"] == "OVER-DISPERSED"]
adeq = [r for r in cells if r["m65_verdict"] == "GAUSSIAN NOMINAL ADEQUATE"]
assert all(r["pm1_state"] == "over" for r in over)
assert all(r["pm2_state"] == "under" for r in adeq)
over_pm2_under = sum(r["pm2_state"] == "under" for r in over)
cnt = n8["reading"]["counts"]
assert cnt["near-Gaussian"] == 0 and len(cells) == 48 and len(over) == m65["verdict"]["counts"]["OVER-DISPERSED"]
rel = n8["cells"]["released_ckpt_ens5 [epistemic] all ten episodes"]["by_horizon"]
xw = {c["id"]: c for c in J("results/version_crosswalk.json")["claims"]}
for k in ("rwm_table_decay", "rwmu_table_decay", "rwm_table_iterations", "rwmu_table_iterations", "rwmu_shared_trunk"):
    assert k in xw, k
assert xw["rwm_table_decay"]["v1"]["table"] == "Table S9" and xw["rwmu_table_decay"]["v1"]["table"] == "Table S8"
assert "1.0" in xw["rwm_table_decay"]["v1"]["fragment"] and "1.0" in xw["rwmu_table_decay"]["v1"]["fragment"]
o12 = J("results/step6_3_min_logstd.json")
assert o12["armA_rate_min_logstd"] < 0 and o12["rate_ratio"] > 1
q1 = J("results/q1_pets_descendants.json")["counts"]
looked = q1["examined"] + q1["construction_absent_and_so_out_of_scope"]
assert q1["carry_the_construction"] == q1["examined"] and q1["inherits"] == 1
rl = lambda c: f"{c['m65_verdict']}"

S22 = f"""### S-22 — M-65's reading "NOT HEAVY-TAILED, in every one of 48 model × horizon cells" · **NEW**
**Retracts** `M-65`, its returned reading and the conclusions drawn from it; `M-96`, its sentence that M-65's reading stands
**What is retracted:** M-65's discharge reading "NOT HEAVY-TAILED, in every one of 48 model x horizon cells"; its conclusion that
"the Gaussian nominal is defensible, and the paper's attribution of the coverage shortfall to scale rather than to distributional
shape is not an assumption but a measurement"; and its use of the oracle constant's growth with horizon to argue that "no single
lambda repairs" the penalty. M-96's sentence that "M-65's returned reading stands as it was".

**Why: M-65 read the tails backwards.** Rescaling σ so that mean|error|/σ equals a Gaussian's √(2/π) makes a heavy-tailed (or
scale-mixture) error over-cover at ±1σ and under-cover at ±2σ. M-65's committed branches read ±1σ only, and named over-coverage
OVER-DISPERSED; over-coverage at ±1σ is the first half of the heavy-tail signature, not over-dispersion. N8 (`R-81`) reads the
second half, from the same stored errors: of the {len(cells)} cells, {cnt['heavy-tailed']} are heavy-tailed (±1σ over and ±2σ under),
{cnt['mixed']} mixed and {cnt['near-Gaussian']} near-Gaussian. Every one of the {len(over)} cells M-65 called OVER-DISPERSED over-covers at
±1σ, and {over_pm2_under} of them under-cover at ±2σ; every one of the {len(adeq)} it called GAUSSIAN NOMINAL ADEQUATE under-covers at
±2σ. The λ argument is withdrawn with it, for a separate reason: MOPO's penalty is meant to bound one-step model error at visited
states, so a constant that grows with horizon on accumulated error does not show that no single λ serves that purpose.

**What is not retracted.** M-65's branch labels as the committed rule returned them (in `results/m65_gaussian_nominal.json`), its
oracle constants (`R-81` reports them as c beside the coverage-matching multiplier k), and M-96's correction that two in-band cells
fall below 68.27%.

**What replaces it:** `R-81`. The quantity the paper calls "too small by" is now the coverage-matching multiplier k (DECISIONS Y7):
on the released checkpoint's epistemic term, all ten episodes, k = {rel['1']['k_coverage_matching']:.1f} at h = 1,
{rel['100']['k_coverage_matching']:.1f} at h = 100 and {rel['368']['k_coverage_matching']:.1f} at h = 368, against the mean-matching
c = {rel['1']['c_mean_matching']:.1f}, {rel['100']['c_mean_matching']:.1f} and {rel['368']['c_mean_matching']:.1f}.

**Who found it:** the TMLR review of 19 October 2026 (PLAN round 5, Annex 1 item 24a); measured by N8 in session G4.
**Evidence** `RUN` `results/n8_tails.json`, `results/m65_gaussian_nominal.json`.
**Status** CONFIRMED · **Relevance** METHOD
"""

S23 = f"""### S-23 — The shared state trunk presented as something the follow-up does not state · **NEW**
**Retracts** — the framing of `C-04`, filed among the `C-` entries ("paper says one thing, code does another") with "ensemble of 5"
in quotation marks, as if the follow-up's ensemble were described as independent models
**What is withdrawn:** the presentation, not the fact. RWM-U v1 §4.1 states the construction: "{xw['rwmu_shared_trunk']['v1']['fragment']}"
(unchanged in {', '.join(xw['rwmu_shared_trunk']['current_fragment_present_in'])}; `results/version_crosswalk.json`, `rwmu_shared_trunk`).
So the shared state trunk is documented, and the paper credits it to the follow-up rather than presenting it as a finding.
**What stands:** C-04's facts (one state trunk, one auxiliary trunk, heads replicated), X-12's topology and parameter counts, and X-12's
point that the ensemble mean is fed back through one recurrent state, which is also the rollout the follow-up describes. Whether the
follow-up states the auxiliary trunk's sharing was not checked here.
**Who found it:** the TMLR review of 19 October 2026; PREMISES P10 (session G1).
**Evidence** `SRC` `results/version_crosswalk.json`.
**Status** CONFIRMED · **Relevance** METHOD
"""

S24 = f"""### S-24 — "The floor it closes onto freezes, and nothing can reopen it" · **NEW**
**Retracts** — the last sentence of `C-11`: "So once the interval starts closing, the floor it closes onto freezes, and nothing can reopen it."
**Why:** C-11's own algebra shows that `state_min_logstd` takes no gradient from the bound term, and C-11 itself notes that it is reachable
through the σ path in the state loss. It is: on Arm A it moves at {o12['armA_rate_min_logstd']:.3e} per iteration, {o12['rate_ratio']:.1f} times
more slowly than `log_delta_logstd` (`results/step6_3_min_logstd.json`, `armA_rate_min_logstd`, `rate_ratio`), and the released checkpoint's
floor has travelled {o12['distance_travelled']:.2f} from its initialisation. "Freezes" overstates it; the correct statement is that the floor
receives no gradient from the bound term and moves only through the state loss, slowly.
**What stands:** C-11's algebra and its zero-gradient measurement.
**Who found it:** the TMLR review of 19 October 2026 (PLAN round 5, Annex 1 item 29).
**Evidence** `RUN` `results/step6_3_min_logstd.json`; `SRC` `system_dynamics.py:301-302`.
**Status** CONFIRMED · **Relevance** METHOD
"""

C17 = f"""### C-17 — C-09 corrected: both papers set the decay factor to 1.0, which is what the code computes · **NEW**
**Corrects** C-09, whose last sentence says "the paper describes a hyperparameter the code does not have".
Both originals name α "a decay factor" in the multi-step loss and set it to 1.0 in their training tables: RWM v1 {xw['rwm_table_decay']['v1']['table']}
("{xw['rwm_table_decay']['v1']['fragment']}"; {xw['rwm_table_decay']['current']['table']} in {xw['rwm_table_decay']['current']['version']}) and RWM-U v1
{xw['rwmu_table_decay']['v1']['table']} ({xw['rwmu_table_decay']['current']['table']} in {xw['rwmu_table_decay']['current']['version']})
(`results/version_crosswalk.json`, `rwm_table_decay`, `rwmu_table_decay`). With α = 1.0 every forecast step has equal weight, which is the
unweighted mean C-09 found in the code. C-09's fact stands, no α parameter exists in the code, but it is a naming difference, a parameter set
to no decay and not implemented as a parameter, and nothing numerical differs between paper and code.
**The training length** is in the same tables: 2,500 iterations at learning rate 1e-4 in RWM v1 {xw['rwm_table_iterations']['v1']['table']}
and RWM-U v1 {xw['rwmu_table_iterations']['v1']['table']} ({xw['rwmu_table_iterations']['current']['table']} in {xw['rwmu_table_iterations']['current']['version']})
(`rwm_table_iterations`, `rwmu_table_iterations`). A citation of "Table S9" for the training length is right for RWM v1 and wrong for the
follow-up, whose table is S8 in v1.
**Evidence** `SRC` `results/version_crosswalk.json`; `docs/presubmission/round5/PREMISES.md` (P13–P15).
**Status** CONFIRMED · **Relevance** METHOD
"""

C18 = """### C-18 — "Bootstrap ensembles": per-head resampling is in the online training path and not in the offline one · **NEW**
RWM-U v1 §4.1 calls the ensemble "bootstrap ensembles". The released code resamples per head in one of its two training paths:
`rsl_rl_rwm/rsl_rl/modules/system_dynamics.py:129-140` gives `compute_loss` a `bootstrap` flag, default False, under which each head draws its
own with-replacement resample of the batch (`torch.randint(0, B, (B,))`), and `rsl_rl_rwm/rsl_rl/algorithms/mbpo_ppo.py:213` sets it in the
MBPO-PPO model update. The offline path, `robotic_world_model_lite/scripts/model_training.py:68,159`, calls `compute_loss` without it, so every
head sees the same batch and the heads differ only in initialisation. Our arms follow the offline path: `scripts/step5_train.py:259` calls
our `compute_loss` without `bootstrap`. So "bootstrap" is a gap between the paper and the offline path only. Which path trained the released
checkpoint is not recorded (`R-86`).
**Evidence** `SRC` `system_dynamics.py:129-140`, `mbpo_ppo.py:213`, `model_training.py:68,159`, `scripts/step5_train.py:259`; `docs/presubmission/round5/PREMISES.md` (P12).
**Status** CONFIRMED · **Relevance** CONTRIB
"""

R89 = f"""### R-89 — R-75's survey counts, stated without the circular "examined" · **NEW**
**Corrects** R-75's count sentence, "Of 10 repositories examined on 2026-09-20 under a protocol fixed before the search, 10 carry the
construction and 1 of those trains it against a sampled squared error". The protocol counts as examined only the repositories that carry
the construction (`results/q1_search_protocol.md` §3), so "10 examined, 10 carry" is one count stated twice. The three counts, from
`results/q1_pets_descendants.json` `counts`: **{looked} repositories looked at** ({q1['examined']} with the construction and
{q1['construction_absent_and_so_out_of_scope']} without it, set aside as out of scope); **{q1['carry_the_construction']} implement the
construction**; **{q1['inherits']} trains it against a sampled squared error, and only optionally** (`nirbhayjm/va_mbpo`, in its value-aware
mode, not its default). R-75's reading, that the substitution is rare among the descendants examined, stands.
**Evidence** `RUN` `results/q1_pets_descendants.json`; `SRC` `results/q1_search_protocol.md`.
**Status** CONFIRMED · **Relevance** CONTRIB
"""

# ------------------------------------------------------------------ the Status lines (sanctioned in-place edits)
m65_old = "**Status** PRE-REGISTERED, DISCHARGED · **Relevance** METHOD"
blk65 = led.split("### M-65 ", 1)[1].split("\n### ", 1)[0]
assert blk65.count(m65_old) == 1
m65_new = "**Status** PRE-REGISTERED, DISCHARGED; its returned reading SUPERSEDED by `S-22` (see `R-81`) · **Relevance** METHOD"
blk96 = led.split("### M-96 ", 1)[1].split("\n### ", 1)[0]
m96_old = "**Status** CONFIRMED · **Relevance** METHOD"
assert blk96.count(m96_old) == 1
m96_new = "**Status** CONFIRMED; SUPERSEDED IN PART by `S-22` (its sentence that M-65's reading stands) · **Relevance** METHOD"

os.makedirs(EV, exist_ok=True)
shutil.copy(L, os.path.join(EV, "FINDINGS_LEDGER.md.before_G5"))
shutil.copy(RES, os.path.join(EV, "RESULTS.md.before_G5"))
new_led = led.replace("### M-65 " + blk65, "### M-65 " + blk65.replace(m65_old, m65_new), 1)
new_led = new_led.replace("### M-96 " + blk96, "### M-96 " + blk96.replace(m96_old, m96_new), 1)
assert new_led.count(m65_new) == 1 and new_led.count(m96_new) == 1
new_led = new_led.rstrip("\n") + "\n\n" + "\n".join((S22, S23, S24, C17, C18, R89))
open(L, "w", encoding="utf-8").write(new_led)

rows = {"S": (21, 24), "C": (16, 18), "R": (88, 89)}
for pfx, (a, b) in rows.items():
    m = re.search(rf"^(\| `{pfx}-` [^|]*\| ){a}( \|)", res, re.M)
    assert m, pfx
    res = res.replace(m.group(0), f"{m.group(1)}{b}{m.group(2)}", 1)
old_ex = "see the variance collapse (`C-10`, `C-11`) and the absent decay factor (`C-09`)"
assert res.count(old_ex) == 1
res = res.replace(old_ex, "see the variance collapse (`C-10`, `C-11`) and the offline path's missing per-head resampling (`C-18`)")
open(RES, "w", encoding="utf-8").write(res)
print("appended S-22, S-23, S-24, C-17, C-18, R-89; M-65 and M-96 Status lines set; RESULTS.md rows moved")
