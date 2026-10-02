"""T2: record rule X1's Part A reading in a new ledger entry, exactly as scripts/rssm_diagnostics.py
returned it, with Part B's descriptive values; every figure read from results/rssm_diagnostics.json.
Keeps RESULTS.md's M- row in step. Run from the repository root."""
import json, re
L = "FINDINGS_LEDGER.md"; led = open(L, encoding="utf-8").read()
assert "rssm_diagnostics.json` returns" not in led
d = json.load(open("results/rssm_diagnostics.json"))
nxt = max(int(n) for n in re.findall(r"^### M-(\d+) ", led, re.M)) + 1
H = d["arena"]["horizons"]; fm = d["floor_mean"]
rows = []
for k in ("rssm_tf_s7", "rssm_ar_s7"):
    for how in ("mode", "expected", "sampled"):
        v = d["part_a"][k]["three_seed_mean"][how]; bf = d["part_a"][k]["below_floor_at_h32"][how]
        rows.append(f"| {k} | {how} | " + " | ".join(f"{v[h]:.4f}" for h in H) + f" | {'yes' if bf['below'] else 'no'} |")
pb = d["part_b"]
brows = [f"| {k.replace('|', ', ')} | {v['2500']['mean_over_steps']['one_step_rel_l1_prior']:.4f} | {v['2500']['mean_over_steps']['one_step_rel_l1_posterior']:.4f} | "
         f"{v['2500']['mean_over_steps']['prior_over_posterior']:.2f} | {v['2500']['mean_over_steps']['kl']:.2f} | {v['500']['mean_over_steps']['prior_over_posterior']:.2f} | {v['500']['mean_over_steps']['kl']:.2f} |"
         for k, v in pb.items()]
e = f"""
### M-{nxt} — Rule X1 (M-80), Part A: `results/rssm_diagnostics.json` returns {d['part_a_reading']} · **NEW**
**Records** M-80's Part A reading, exactly as `scripts/rssm_diagnostics.py --part ab` returned it, as committed
before the reading existed (commit `2433f44`). It does not discharge M-80: the final reading waits on Part C,
which this reading opens (ruling U2 allows it). Exploratory; M-75 and M-76 are unchanged.

**Part A.** Held-out pair, relative-L1, 3-seed mean; hold-last floor
{', '.join(f'h = {h} {fm[h]:.4f}' for h in H)}. The mode read-out reproduces `results/baselines_eval.json`
(max difference {d['part_a_mode_reproduces_baselines_eval']['max_abs_diff']:.1e}) and equals the model's own rollout.

| model | read-out | {' | '.join('h = ' + h for h in H)} | below the floor at h = 32 |
|---|---|{'---|' * len(H)}---|
""" + "\n".join(rows) + f"""

The teacher-forced RSSM's expected and sampled read-outs lower its error at every horizon, but neither is below
the floor at h = 32, so the rule returns **{d['part_a_reading']}**: reading the forecast differently does not
rescue it.

**Part B, descriptive.** Over the 32 history steps, one row per run and seed: one-step decoded relative-L1 from the
prior's and the posterior's mode latents at the same GRU state, their ratio, and KL(posterior ‖ prior) per step
(nats), at 2,500 iterations and at 500:

| run | prior | posterior | prior / posterior | KL | prior / posterior @ 500 | KL @ 500 |
|---|---|---|---|---|---|---|
""" + "\n".join(brows) + """
**Evidence** `RUN` `results/rssm_diagnostics.json`; `SRC` `scripts/rssm_diagnostics.py`.
**Status** CONFIRMED · **Relevance** METHOD
"""
open(L, "w", encoding="utf-8").write(led.rstrip("\n") + "\n" + e)
R = open("RESULTS.md", encoding="utf-8").read()
m = re.search(r"^(\|\s*`M-`[^|]*\|\s*)(\d+)(\s*\|)", R, re.M); assert m and int(m.group(2)) == nxt - 1
open("RESULTS.md", "w", encoding="utf-8").write(R[:m.start()] + m.group(1) + str(nxt) + m.group(3) + R[m.end():])
print(f"appended M-{nxt}; RESULTS.md M- row {nxt-1} -> {nxt}")
