"""
N12 (round 5; POST HOC) -- what is known about the data the released checkpoint trained on, and which numbers change role
under each reading. docs/presubmission/round5/PROTOCOLS.md §5 N12 is the specification; this is a summary. Descriptive; no
verdict; it re-opens no rule.

SOURCE EVIDENCE (quoted with file:line): the release's configured dataset location; the README's asset list; the checkpoint
file's top-level keys, `iter`, `infos`, and whether any data statistic, hash or path is stored (and its SHA-256); the upstream
tags. The correspondence is quoted only as Appendix F already quotes it (the exchange is kept outside the repository).
DATA. One-step error, relative-L1 at h = 1 on M-64's short units (m64_short_units.build_index(episodes, 1), unit_rollout,
rel_l1, as x3_cross_fold.m64_units uses them): the released checkpoint on each of the ten episodes; Arm A seeds 0-2 at 2,500
iterations (default split; seed mean per unit) on each training and each held-out episode. Per-episode means; pooled means;
unit-level intervals (m64_short_units.boot_ci: 20,000 draws, default_rng(0)).
ASSERTION, first: x3_cross_fold.assert_f, unchanged -- Arm A and Arm B seed-mean per-unit values on the held-out pair
reproduce results/m64_short_units.json cells.C_section_5_ab_gap (maximum absolute difference 0.0).
ROLE LIST: every results/*.json whose text labels the released checkpoint's arena in-sample (the search strings are fixed in
ROLE_TERMS below), i.e. whose role flips if the CSV is a separate recording.
Writes results/n12_provenance.json. Run from the repository root.
"""
import glob
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np  # noqa: E402
import torch  # noqa: E402
import rwm_data as R  # noqa: E402
import rollout_eval as E  # noqa: E402
import score_reference as S  # noqa: E402
import m64_short_units as M64  # noqa: E402
import x3_cross_fold as X3  # noqa: E402
import x11_common as C  # noqa: E402

OUT = os.path.join(R.RESULTS, "n12_provenance.json")
LITE = os.path.join(C.ROOT, os.pardir, "robotic_world_model_lite")
ROLE_TERMS = ("trained on all ten", "released_ckpt_arena_is_in_sample", "in-sample for the released", "in-sample for the checkpoint",
              "in_sample_for_released", "in-sample for it", "its own training data")
MODULES = ("scripts/n12_provenance.py", "scripts/m64_short_units.py", "scripts/x3_cross_fold.py", "scripts/x11_common.py",
           "src/score_reference.py")


def quote(path, lines):
    L = open(path, encoding="utf-8").read().split("\n")
    return {"file": os.path.relpath(path, C.ROOT), "lines": f"{lines[0]}-{lines[-1]}",
            "text": [L[i - 1] for i in range(lines[0], lines[-1] + 1)]}


def grep_lines(path, pat):
    out = []
    for i, line in enumerate(open(path, encoding="utf-8").read().split("\n"), 1):
        if re.search(pat, line):
            out.append({"line": i, "text": line.strip()})
    return {"file": os.path.relpath(path, C.ROOT), "matches": out}


def per_unit(model, starts):
    cfg, data, _ = C.data()
    return M64.rel_l1(*M64.unit_rollout(model, data, cfg, starts, 1, False)[3:5])


def main():
    os.chdir(C.ROOT)
    t0 = time.perf_counter()
    cfg, data, ep = C.data()
    af = X3.assert_f(cfg, data, (0, 1, 2))
    A = {"m64_cell_C": {**af, "pass": bool(af["pass"] and af["max_abs_diff"] == 0.0)}}
    print(f"  assertion m64_cell_C: {'PASS' if A['m64_cell_C']['pass'] else 'FAIL'} {af['max_abs_diff']}")
    if not A["m64_cell_C"]["pass"]:
        C.blocked(OUT, "the reproduction assertion failed", assertions=A)

    # ---------------- source evidence ----------------
    ck = R.repo_paths()["ckpt"]
    obj = torch.load(ck, map_location="cpu")
    top = {k: type(v).__name__ for k, v in obj.items()}
    sd = obj["system_dynamics_state_dict"]
    data_like = [k for k in list(obj.keys()) + list(sd.keys())
                 if re.search(r"mean|std|norm|data|hash|path|csv|episode", k, re.I) and not re.search(r"logstd", k, re.I)
                 and not re.search(r"_layers\.\d+\.(weight|bias)$", k)]       # network parameters are not data statistics
    tags = subprocess.run(["git", "-C", LITE, "tag", "--list"], capture_output=True, text=True).stdout.split()
    head = subprocess.run(["git", "-C", LITE, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    src = {"dataset_location": [quote(os.path.join(LITE, "scripts", "configs", "anymal_d_flat_cfg.py"), (36, 37)),
                                quote(os.path.join(LITE, "scripts", "configs", "base_cfg.py"), (33, 34))],
           "readme_assets": grep_lines(os.path.join(LITE, "README.md"), r"assets|\.csv|\.pt"),
           "checkpoint": {"file": os.path.relpath(ck, C.ROOT), "sha256": C.sha256(ck), "top_level_keys": top,
                          "iter": obj.get("iter"), "infos": obj.get("infos"),
                          "keys_that_could_hold_data_statistics_or_provenance": data_like,
                          "has_data_statistics_or_provenance": bool(data_like)},
           "upstream": {"robotic_world_model_lite_head": head, "tags": tags},
           "correspondence": ("quoted only as the paper's Appendix F quotes it; the anonymised exchange is kept outside the "
                              "repository and is not re-quoted here")}
    print(f"  checkpoint keys {list(top)}; iter {obj.get('iter')}; infos {obj.get('infos')}; data-like keys {data_like}")

    # ---------------- data ----------------
    split = E.make_split(seed=0, strat_path=C.STRAT, verbose=False)
    train, hold = sorted(split["train_episodes"]), sorted(split["holdout_episodes"])
    rel = S.ReferenceRWM(obj["system_dynamics_state_dict"])
    rel.eval()
    arms = [X3.load(cfg, C.single_weights((1, 8), s)) for s in (0, 1, 2)]
    per_ep = {}
    for e in range(R.N_EPISODES):
        st_, ue, from_len, n_built = M64.build_index([e], 1)
        assert from_len == n_built, (e, from_len, n_built)
        r_rel = per_unit(rel, st_)
        r_arm = np.mean([per_unit(m, st_) for m in arms], 0)
        per_ep[e] = {"n_units": int(n_built), "released": r_rel, "armA": r_arm,
                     "role_for_armA": "in-sample" if e in train else "held-out"}
    def pooled(key, eps):
        v = np.concatenate([per_ep[e][key] for e in eps])
        u = np.concatenate([[e] * per_ep[e]["n_units"] for e in eps])
        ci_u, ci_e = M64.boot_ci(v, None, u, 0)
        return {"mean": float(v.mean()), "ci_unit_level": ci_u, "ci_episode_level": ci_e, "n_units": int(len(v)),
                "episodes": list(eps)}
    data_out = {"metric": "relative-L1 at h = 1 on M-64's 33-row units (m64_short_units.rel_l1)",
                "per_episode": {str(e): {"n_units": v["n_units"], "released_mean": float(v["released"].mean()),
                                         "armA_seed_mean": float(v["armA"].mean()), "armA_role": v["role_for_armA"]}
                                for e, v in per_ep.items()},
                "released_all_ten": pooled("released", range(R.N_EPISODES)),
                "released_on_armA_training_episodes": pooled("released", train),
                "released_on_armA_heldout_episodes": pooled("released", hold),
                "armA_in_sample": pooled("armA", train), "armA_held_out": pooled("armA", hold)}

    # ---------------- which artifacts change role ----------------
    hits = []
    for p in sorted(glob.glob(os.path.join(R.RESULTS, "*.json"))):
        try:
            txt = open(p, encoding="utf-8").read()
        except UnicodeDecodeError:
            continue
        found = [t for t in ROLE_TERMS if t in txt]
        if found and "released" in txt:
            hits.append({"artifact": os.path.relpath(p, C.ROOT), "terms": found})
    hits = [h for h in hits if os.path.basename(h["artifact"]) != "n12_provenance.json"]
    out = {"analysis": "N12", "post_hoc": True, "descriptive": True,
           "never_reopens": "any rule; nothing here changes a verdict",
           "script": "scripts/n12_provenance.py", "script_sha256": C.sha256("scripts/n12_provenance.py"),
           "assertions": A, "source_evidence": src, "one_step_error": data_out,
           "role_change": {"search_terms": list(ROLE_TERMS),
                           "rule": "a results/*.json whose text labels the released checkpoint's arena in-sample",
                           "artifacts": hits, "n": len(hits),
                           "if_separate_recording": "every released-checkpoint number in these artifacts is held-out, not in-sample"},
           "what_is_known": ("no file in either repository records which rows trained the released checkpoint; the checkpoint "
                             "stores no data statistic, hash or path (see source_evidence.checkpoint); the configured dataset "
                             "location is the release's own assets folder, which holds the CSV this project uses"),
           "code_sha256": {p: C.sha256(p) for p in MODULES},
           "git_head": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
           "timing": {"wall_clock_s": time.perf_counter() - t0, "cpu_count": os.cpu_count()}}
    json.dump(out, open(OUT, "w"), indent=1, default=str)
    d = data_out
    print(f"  released all ten {d['released_all_ten']['mean']:.4f} {d['released_all_ten']['ci_unit_level']}; "
          f"armA in {d['armA_in_sample']['mean']:.4f} {d['armA_in_sample']['ci_unit_level']}, "
          f"out {d['armA_held_out']['mean']:.4f} {d['armA_held_out']['ci_unit_level']}; "
          f"released on train eps {d['released_on_armA_training_episodes']['mean']:.4f}, held-out eps "
          f"{d['released_on_armA_heldout_episodes']['mean']:.4f}; role-change artifacts {len(hits)}")
    print(f"  wrote {R.rel(OUT)}")


if __name__ == "__main__":
    main()
