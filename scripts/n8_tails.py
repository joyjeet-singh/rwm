"""
N8 (round 5; POST HOC) -- the tails, correcting M-65's reading. docs/presubmission/round5/PROTOCOLS.md §5 N8 is the
specification; this is a summary. Post hoc: computed after M-65's data existed. It never re-opens M-65 or any rule and
changes no verdict; it reports beside M-65's verdict what its cells look like at +-2 sigma.

INPUT. M-65's eight cases x six horizons = 48 cells, read from the per-triple cache through
m65_gaussian_nominal.load (m65_gaussian_nominal.py:55-62), seeds concatenated as there. No rollout.
PER CELL. M-65's mean-matching constant c = rho / sqrt(2/pi) and the +-1 and +-2 sigma coverage under c*sigma (M-65's own
arithmetic, m65_gaussian_nominal.py:122-136). The COVERAGE-MATCHING multiplier k, over the elements with finite sigma > 0:
with r = e / sigma and N elements, k = r_(ceil(0.6827 N)), the smallest k with mean(r <= k) >= 0.6827 -- the value
task_d3_perhorizon.fit_scalar's bisection converges to; k / c; and the +-2 sigma coverage under k*sigma, mean(r <= 2k).
SIGNATURE (tolerances fixed in PROTOCOLS before this ran): +-1 sigma over if coverage under c*sigma > 73.27%, under if
< 63.27%, else within; +-2 sigma over if > 97.95%, under if < 92.95%, else within. heavy-tailed = +-1 over and +-2 under;
light-tailed = +-1 under and +-2 over; near-Gaussian = both within; otherwise mixed (+-1 <state>, +-2 <state>).
ASSERTIONS, before any reading: (1) rho, c and both coverages under c*sigma equal m65_gaussian_nominal.json for all 48
cells within 1e-12; (2) for released_ckpt_ens5 [epistemic] all ten episodes, k equals task_d3_perhorizon.fit_scalar on
the same arrays (left-padded with 32 NaN columns) at every horizon, relative 1e-9.
Writes results/n8_tails.json. Run from the repository root.
"""
import json
import math
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import rwm_data as R  # noqa: E402
import m65_gaussian_nominal as M65  # noqa: E402
import task_d3_perhorizon as TD3  # noqa: E402
import x11_common as C  # noqa: E402

OUT = os.path.join(R.RESULTS, "n8_tails.json")
TOL1, TOL2 = 1e-12, 1e-9
T1, T2 = M65.TARGET1, M65.TARGET2
BAND1, BAND2 = 5.0, 2.5
KTARGET = TD3.TARGET
MODULES = ("scripts/n8_tails.py", "scripts/m65_gaussian_nominal.py", "scripts/task_d3_perhorizon.py",
           "src/per_triple_cache.py", "scripts/x11_common.py")
ASSERT_CELL = "released_ckpt_ens5 [epistemic] all ten episodes"


def state(cov, target, band):
    return "over" if cov > target + band else "under" if cov < target - band else "within"


def signature(s1, s2):
    if s1 == "over" and s2 == "under":
        return "heavy-tailed"
    if s1 == "under" and s2 == "over":
        return "light-tailed"
    if s1 == "within" and s2 == "within":
        return "near-Gaussian"
    return f"mixed (±1σ {s1}, ±2σ {s2})"


def k_of(e, g):
    v = np.isfinite(g) & (g > 0) & np.isfinite(e)
    r = np.sort((e[v] / g[v]).ravel())
    n = r.size
    return float(r[math.ceil(KTARGET * n) - 1]), int(n), r


def main():
    os.chdir(C.ROOT)
    t0 = time.perf_counter()
    m65 = json.load(open(os.path.join(R.RESULTS, "m65_gaussian_nominal.json")))
    cells, d1, d2 = {}, 0.0, 0.0
    for slug, arena, seeds, term, n_ind in M65.CASES:
        e, g = M65.load(slug, arena, seeds, term)
        label = f"{slug} [{term}] {arena}"
        stored = m65["cases"][label]["by_horizon"]
        rows = {}
        for h in M65.HS:
            eh, gh = e[:, :h], g[:, :h]
            me, mg = float(np.nanmean(eh)), float(np.nanmean(gh))
            rho = me / mg
            c = rho / M65.CALIB
            cov1 = float(np.nanmean(eh <= c * gh) * 100.0)
            cov2 = float(np.nanmean(eh <= 2 * c * gh) * 100.0)
            w = stored[str(h)]
            d1 = max(d1, abs(rho - w["rho_err_over_sigma"]), abs(c - w["oracle_constant_c"]),
                     abs(cov1 - w["coverage_pm1_oracle_pct"]), abs(cov2 - w["coverage_pm2_oracle_pct"]))
            k, n, r = k_of(eh, gh)
            if label == ASSERT_CELL:
                pad = np.full((eh.shape[0], TD3.START, eh.shape[2]), np.nan)
                kb = TD3.fit_scalar(np.concatenate([pad, eh], 1), np.concatenate([pad, gh], 1), h)
                d2 = max(d2, abs(k - kb) / abs(kb))
            s1, s2 = state(cov1, T1, BAND1), state(cov2, T2, BAND2)
            rows[str(h)] = {"rho": rho, "c_mean_matching": c, "cov1_at_c_pct": cov1, "cov2_at_c_pct": cov2,
                            "k_coverage_matching": k, "k_over_c": k / c,
                            "cov1_at_k_pct": float(100 * np.mean(r <= k)), "cov2_at_k_pct": float(100 * np.mean(r <= 2 * k)),
                            "n_elements": n, "pm1_state": s1, "pm2_state": s2, "signature": signature(s1, s2),
                            "m65_verdict": w["verdict"]}
        cells[label] = {"model_id": slug, "arena": arena, "sigma_term": term, "seeds": list(seeds),
                        "n_independent": n_ind, "by_horizon": rows}
    assertions = {"1": {"pass": bool(d1 <= TOL1), "max_abs_diff": d1, "tolerance": TOL1,
                        "against": "results/m65_gaussian_nominal.json cases[*].by_horizon[h] (48 cells)"},
                  "2": {"pass": bool(d2 <= TOL2), "max_rel_diff": d2, "tolerance": TOL2,
                        "against": f"task_d3_perhorizon.fit_scalar on {ASSERT_CELL}"}}
    for k_, v in assertions.items():
        print(f"  assertion ({k_}): {'PASS' if v['pass'] else 'FAIL'}  {v.get('max_abs_diff', v.get('max_rel_diff'))}")
    if not all(v["pass"] for v in assertions.values()):
        C.blocked(OUT, "a reproduction assertion failed", assertions=assertions)
    sigs = [r["signature"] for c_ in cells.values() for r in c_["by_horizon"].values()]
    counts = {"heavy-tailed": sigs.count("heavy-tailed"), "light-tailed": sigs.count("light-tailed"),
              "near-Gaussian": sigs.count("near-Gaussian"),
              "mixed": sum(1 for s in sigs if s.startswith("mixed"))}
    mixed_detail = {}
    for s in sigs:
        if s.startswith("mixed"):
            mixed_detail[s] = mixed_detail.get(s, 0) + 1
    cross = {}
    for c_ in cells.values():
        for r in c_["by_horizon"].values():
            key = f'{r["m65_verdict"]} -> {r["signature"]}'
            cross[key] = cross.get(key, 0) + 1
    out = {"analysis": "N8", "post_hoc": True,
           "never_reopens": "M-65 (its verdict and counts stand as committed) or any discharged rule; nothing here changes a verdict",
           "script": "scripts/n8_tails.py", "script_sha256": C.sha256("scripts/n8_tails.py"),
           "design": {"cells": len(sigs), "tolerances": {"pm1_pts": BAND1, "pm2_pts": BAND2},
                      "targets_pct": [T1, T2], "k_definition": "r_(ceil(0.6827 N)) over elements with finite sigma > 0",
                      "specification": "docs/presubmission/round5/PROTOCOLS.md §5 N8"},
           "assertions": assertions, "cells": cells,
           "reading": {"counts": counts, "n_cells": len(sigs), "mixed_detail": mixed_detail,
                       "m65_counts": m65["verdict"]["counts"], "m65_verdict_to_signature": cross},
           "code_sha256": {p: C.sha256(p) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "timing": {"wall_clock_s": time.perf_counter() - t0, "cpu_count": os.cpu_count()}}
    json.dump(out, open(OUT, "w"), indent=1)
    print(f"  N8: {counts} of {len(sigs)}; M-65 -> signature {cross}")
    print(f"  wrote {R.rel(OUT)}")


if __name__ == "__main__":
    main()
