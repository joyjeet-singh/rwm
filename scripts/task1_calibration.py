"""
Task 1 -- does the corrected objective produce a USABLE uncertainty estimate?

1a calibration, 1b input-dependence, 1c the unreachability result.

PREDICTION, stated before the numbers (the brief's expected shape):
  the faithful arm's sigma is a learned constant near 6.4e-03 in normalised units while
  typical errors are two orders of magnitude larger, so its coverage should be near ZERO
  and should not improve with horizon. If the NLL arm lands near 68/95 at short horizon
  and degrades with horizon, that is a working uncertainty estimate with an honest
  limitation. If it lands nowhere near either, the collapse reversed WITHOUT producing
  calibration -- also a result.
"""
import json, os, sys, math
from math import comb


def _sign_p(k, n):
    """Two-sided exact binomial tail probability under p = 0.5."""
    if n == 0:
        return float("nan")
    tail = (sum(comb(n, i) for i in range(k, n + 1)) if k * 2 >= n
            else sum(comb(n, i) for i in range(0, k + 1)))
    return min(1.0, 2.0 * tail / 2 ** n)

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np, torch
import rwm_data as R, rollout_eval as E, rwm_metrics as MET, rwm_model as M, score_reference as S
START=E.START_STEP; SEEDS=(0,1,2); HS=(1,8,32,128,368)
GROUPS=[("base lin vel",R.LIN_VEL),("base ang vel",R.ANG_VEL),("proj gravity",R.GRAVITY),
        ("joint pos",R.JOINT_POS),("joint vel",R.JOINT_VEL),("joint torque",R.JOINT_TAU)]
paths=R.repo_paths(); cfg=R.load_reference_config(paths["lite"])
data,ep=R.load_data(paths["csv"],verbose=False)
split=E.make_split(seed=0,strat_path=os.path.join(R.RESULTS,"step0_strat.json"),verbose=False)
OOS=list(split["holdout_episodes"])
starts=MET.non_overlapping_starts(ep,OOS,400)
idx=np.asarray(starts)[:,None]+np.arange(400)[None,:]
raw=data[idx]
ST=torch.as_tensor(R.normalise_state(raw[:,:,R.STATE_COLS],cfg["state_data_mean"],cfg["state_data_std"]),dtype=torch.float32)
AC=torch.as_tensor(raw[:,:,R.ACTION_COLS],dtype=torch.float32)
def get(tag,s, arm="A"):
    m=M.build_from_config(cfg,ensemble_size=1)
    m.load_state_dict(torch.load(f"runs/arm{arm}_seed{s}{tag}/weights_2500.pt",map_location="cpu")["model_state_dict"],strict=True)
    m.eval(); return m
# Arm B is measured here too. R-52 claimed sigma is input-independent "in all four
# models" while this artifact held three; the teacher-forced arm had no
# cov-of-sigma-across-batch measurement anywhere. Now it does.
MODELS={"faithful (mse)":[get("",s) for s in SEEDS],
        "corrected (nll)":[get("_nll",s) for s in SEEDS],
        "teacher-forced armB":[get("",s,arm="B") for s in SEEDS],
        "released ckpt":[S.ReferenceRWM(torch.load(paths["ckpt"],map_location="cpu")["system_dynamics_state_dict"])]}
print("="*104); print("TASK 1 -- CALIBRATION AND INPUT-DEPENDENCE OF THE PREDICTED SIGMA"); print("="*104)
print(f"  held-out episodes {OOS}, {len(starts)} independent 400-step trajectories, offset=1")
print("  a calibrated Gaussian gives 68.3% at +-1 sigma and 95.4% at +-2 sigma\n")
print("  PREDICTION (stated before the numbers): the faithful arm's coverage should be near")
print("  ZERO and flat in horizon, because its sigma is a learned constant ~6.4e-03 while")
print("  typical errors are two orders of magnitude larger.\n")
out={}
for name,ms in MODELS.items():
    E_,SG=[],[]
    for m in ms:
        pr,sg=m.rollout_full(ST.clone(),AC,START,action_offset=1)
        E_.append((pr[:,START:]-ST[:,START:]).abs().numpy()); SG.append(sg[:,START:].numpy())
    err=np.concatenate(E_,0); sig=np.concatenate(SG,0)          # (n*seeds, T', 45)
    z=err/np.maximum(sig,1e-30)
    rec={"sigma_mean":float(sig.mean()),"err_mean":float(err.mean()),
         "ratio_err_over_sigma":float(err.mean()/sig.mean()),"coverage":{},"groups":{},
         "sigma_by_step":[float(sig[:,:h].mean()) for h in HS]}
    print(f"  {name.upper()}   mean sigma {sig.mean():.3e}   mean |err| {err.mean():.3e}"
          f"   |err|/sigma {err.mean()/sig.mean():.1f}x")
    print(f"    {'h':>5s} {'cov +-1s':>10s} {'dev':>8s} {'cov +-2s':>10s} {'dev':>8s} {'mean sigma':>12s}")
    for h in HS:
        c1=float((z[:,:h]<=1).mean()); c2=float((z[:,:h]<=2).mean())
        rec["coverage"][h]={"pm1":c1,"pm2":c2,"dev1":c1-0.683,"dev2":c2-0.954}
        print(f"    {h:>5d} {100*c1:>9.2f}% {100*(c1-0.683):>+7.1f} {100*c2:>9.2f}%"
              f" {100*(c2-0.954):>+7.1f} {sig[:,:h].mean():>12.3e}")
    for gn,cols in GROUPS:
        c=list(cols)
        rec["groups"][gn]={"pm1":float((z[:,:,c]<=1).mean()),"pm2":float((z[:,:,c]<=2).mean()),
                           "sigma":float(sig[:,:,c].mean()),"err":float(err[:,:,c].mean())}
    print(f"    per group (+-1 sigma coverage): "+"  ".join(
        f"{gn.split()[-1]} {100*rec['groups'][gn]['pm1']:.1f}%" for gn,_ in GROUPS))
    # reliability curve
    zs=[0.25,0.5,0.75,1.0,1.5,2.0,2.5,3.0]
    rec["reliability"]=[{"z":zz,"predicted":math.erf(zz/math.sqrt(2)),
                         "observed":float((z<=zz).mean())} for zz in zs]
    print(f"    reliability (predicted -> observed): "+"  ".join(
        f"{100*r['predicted']:.0f}->{100*r['observed']:.1f}" for r in rec["reliability"]))
    # 1b input dependence
    s0=sig[:, :, :]
    cov_var=(s0.std(axis=0)/np.maximum(s0.mean(axis=0),1e-30)).mean()
    cors=[]
    for d in range(45):
        a=sig[:,:,d].ravel(); b=err[:,:,d].ravel()
        cors.append(np.corrcoef(a,b)[0,1] if a.std()>1e-20 and b.std()>1e-20 else np.nan)
    cors=np.array(cors); fin=cors[~np.isnan(cors)]
    grow=float(sig[:,300:].mean()/max(sig[:,:8].mean(),1e-30))
    rec.update({"cov_of_sigma_across_batch":float(cov_var),
                "sigma_err_corr_mean":float(np.nanmean(cors)),
                "sigma_err_corr_median":float(np.nanmedian(cors)),
                "sigma_err_corr_n_positive":int((fin>0).sum()),"n_finite_corr":int(len(fin)),
                # Two-sided exact binomial against a fair-coin null. Previously the
                # ledger quoted "P ~ 1.4e-06" for 39/45; that is the value for 38/45.
                # Derived here so it cannot drift from the count it describes.
                "sigma_err_corr_sign_p_two_sided":_sign_p(int((fin>0).sum()),int(len(fin))),
                "sigma_growth_late_over_early":grow})
    print(f"    1b  CoV of sigma across batch: {cov_var:.4f}"
          f"   sigma-vs-|err| correlation: mean {np.nanmean(cors):+.3f}"
          f" median {np.nanmedian(cors):+.3f}  positive on {int((fin>0).sum())}/{len(fin)} dims")
    print(f"        sigma growth (late/early forecast steps): {grow:.2f}x\n")
    out[name]=rec
# 1c
print("="*104); print("1c -- THE UNREACHABILITY RESULT"); print("="*104)
nll=[]
for s in SEEDS:
    d=json.load(open(os.path.join(R.RESULTS,f"step5_armA_seed{s}_nll.json")))
    f=d["collapse_fit"]; nll.append((f["slope_per_iter"],f["iters_to_checkpoint_value"]))
print(f"  {'seed':>5s} {'rate/iter':>13s} {'implied iters to -14.4629':>28s}")
for s,(r_,it) in zip(SEEDS,nll): print(f"  {s:>5d} {r_:>+13.4e} {it:>28,.0f}")
print(f"\n  Under gaussian_nll the rate is POSITIVE: log_delta_logstd moves AWAY from the")
print(f"  released checkpoint's value, so the implied iteration count is NEGATIVE")
print(f"  (mean {np.mean([x[1] for x in nll]):,.0f}). No iteration count under this branch")
print(f"  reaches -14.4629. Under sampled MSE it is ~+158,000 (R-43).")
print(f"  => the released checkpoint was trained with the MSE branch.")
out["unreachability"]={"per_seed":[{"seed":s,"rate":r_,"implied_iters":it} for s,(r_,it) in zip(SEEDS,nll)],
                       "mean_implied_iters":float(np.mean([x[1] for x in nll]))}
c_f=out["faithful (mse)"]["coverage"][8]["pm1"]; c_n=out["corrected (nll)"]["coverage"][8]["pm1"]
r_n=out["corrected (nll)"]["sigma_err_corr_mean"]
print("\n"+"="*104); print("  HEADLINE"); print("="*104)
print(f"  faithful  +-1 sigma coverage @h=8: {100*c_f:.2f}%   (calibrated = 68.3%)")
print(f"  corrected +-1 sigma coverage @h=8: {100*c_n:.2f}%")
print(f"  corrected sigma-vs-error correlation: {r_n:+.3f}")
if r_n < 0.1:
    print("  *** FLAG: sigma does NOT correlate with realised error. The collapse reversed")
    print("  *** without producing a usable uncertainty estimate. ***")
else:
    print(f"  sigma correlates with realised error -> the estimate carries information.")
json.dump(out,open(os.path.join(R.RESULTS,"task1_calibration.json"),"w"),indent=2,default=float)
print(f"\n  wrote {R.rel(os.path.join(R.RESULTS,'task1_calibration.json'))}")
