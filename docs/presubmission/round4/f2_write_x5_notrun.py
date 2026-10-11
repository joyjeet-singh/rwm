"""F2 item 1: the ledger entry recording that rule X5 is NOT RUN (PLAN round 4, F2 item 1: "Write one ledger entry
recording why, with no rule"), as the next D- entry, and RESULTS.md's D- row. Every line number is read from the files
X5_FEASIBILITY.md cites; the table itself is round4/X5_FEASIBILITY.md. Writes .bak copies outside the repository and
refuses to run twice. Run from the repository root."""
import os, re, shutil
L, RES, BAK = "FINDINGS_LEDGER.md", "RESULTS.md", "/Users/Shared/rwm_verify/evidence/R4F2"
LITE = "../robotic_world_model_lite/scripts"
at = lambda p, s: next(i + 1 for i, l in enumerate(open(p, encoding="utf-8")) if s in l)
feas = open("docs/presubmission/round4/X5_FEASIBILITY.md", encoding="utf-8").read()
assert "**X5 is NOT RUN.**" in feas
led = open(L, encoding="utf-8").read()
nd = max(int(n) for n in re.findall(r"^### D-(\d+) ", led, re.M)) + 1
DID = f"D-{nd}"
assert DID == "D-38" and "rule X5 is NOT RUN" not in led
ENV = f"{LITE}/envs/anymal_d_flat.py"
entry = f"""
### {DID} — The recorded data hold no velocity command, so the imagination reward cannot be computed from them: rule X5 is NOT RUN · **NEW**
Round 4's rule X5 (PLAN Annex 2; objection O3) would have asked whether the uncertainty penalty the released method applies
covers the model's error in predicted reward over its 100-step imagination horizon, on recorded actions. Its gate, fixed
before any feasibility check: X5 runs only if every term of a reward subset is computable from both the recorded data and the
model's outputs, and the subset must include the two command-tracking terms. This entry records the gate's outcome. It defines
no rule and computes nothing.

**The finding.** The imagination environment's reward (`anymal_d_flat.py:{at(ENV, 'def _compute_imagination_reward_terms')}` in
the lite release) has twelve terms plus the penalty (`base.py:{at(LITE + '/envs/base.py', 'rewards += self.uncertainty_penalty_weight')}`).
The two tracking terms, `track_lin_vel_xy_exp` (`anymal_d_flat.py:{at(ENV, 'track_lin_vel_xy_exp = ')}`) and
`track_ang_vel_z_exp` (`:{at(ENV, 'track_ang_vel_z_exp = ')}`), score the forecast velocity against the environment's own
sampled command, `base_velocity`, drawn at `:{at(ENV, 'def _init_imagination_command')}` and
`:{at(ENV, 'def _reset_imagination_command')}`. The released CSV's 66 columns hold no command: `src/rwm_data.py`'s column map
assigns every one of them to the state, the actions, the contact labels or termination. The command is not a model output
either. Two more terms need it as a gate (`feet_air_time`, `stand_still`). The repository infers the commanded regimes from
achieved base velocity (`scripts/step0_velocity_regimes.py`), but an inferred command is not recorded data. It would also make
the recorded trajectory's tracking reward high by construction, since the command would be fitted to the very velocities the
term scores.

**So X5 is NOT RUN.** No reward subset is defined, and no script or artifact exists for it. The seven terms that are
computable on their own carry none of the reward's purpose, which is to follow the command, and the gate does not allow a
subset without the tracking terms. The term-by-term table, with each term's inputs, weight and dt scaling, is
`docs/presubmission/round4/X5_FEASIBILITY.md`, written by `round4/f2_x5_feasibility.py`.

**What follows.** What the miscalibration costs a policy stays unmeasured, as §11 says. Measuring it needs the commands the
policy was trained on, and so the Isaac Lab data generator (D-36), or a policy trained in imagination, which a CPU cannot
provide. M-70's bound on the penalty's reordering is untouched. The paper states X5's NOT RUN once, with this reason
(PLAN round 4, Annex 6 item 2).
**Evidence** `SRC` `src/rwm_data.py`, `scripts/step0_velocity_regimes.py`; the lite release's `envs/anymal_d_flat.py` and `envs/base.py`.
**Status** CONFIRMED · **Relevance** METHOD
"""
R = open(RES, encoding="utf-8").read()
row = re.search(r"^\| `D-` dataset properties and paper-verification findings \| (\d+) \|", R, re.M)
assert row and int(row.group(1)) == nd - 1, row
R = R.replace(row.group(0), f"| `D-` dataset properties and paper-verification findings | {nd} |", 1)
os.makedirs(BAK, exist_ok=True)
shutil.copy(L, os.path.join(BAK, "FINDINGS_LEDGER.md.x5.bak")); shutil.copy(RES, os.path.join(BAK, "RESULTS.md.x5.bak"))
open(L, "w", encoding="utf-8").write(led.rstrip("\n") + "\n" + entry)
open(RES, "w", encoding="utf-8").write(R)
print(f"appended {DID}; RESULTS.md D- {nd - 1} -> {nd}")
