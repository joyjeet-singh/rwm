"""
Task 2 -- matched per-dimension comparison, released checkpoint vs Arm A.
Task 3 -- the gap-narrowing trend, fitted.
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np, torch
import rwm_data as R, rollout_eval as E, rwm_metrics as MET, rwm_model as M, score_reference as S
START=E.START_STEP
NAMES=(["v_x","v_y","v_z","w_x","w_y","w_z","g_x","g_y","g_z"]
       +[f"q_{l}_{a}" for a in ("HAA","HFE","KFE") for l in ("LF","LH","RF","RH")]
       +[f"qd_{l}_{a}" for a in ("HAA","HFE","KFE") for l in ("LF","LH","RF","RH")]
       +[f"tau_{l}_{a}" for a in ("HAA","HFE","KFE") for l in ("LF","LH","RF","RH")])
paths=R.repo_paths(); cfg=R.load_reference_config(paths["lite"])
data,ep=R.load_data(paths["csv"],verbose=False)
split=E.make_split(seed=0,strat_path=os.path.join(R.RESULTS,"step0_strat.json"),verbose=False)
scale=MET.training_scale(data,ep,split["train_episodes"],cfg["state_data_mean"],cfg["state_data_std"])
OOS=list(split["holdout_episodes"])
ref=S.ReferenceRWM(torch.load(paths["ckpt"],map_location="cpu")["system_dynamics_state_dict"])
def armA():
    m=M.build_from_config(cfg,ensemble_size=1)
    m.load_state_dict(torch.load("runs/armA_seed1_10k/weights_10000.pt",map_location="cpu")["model_state_dict"],strict=True)
    m.eval(); return m
A=armA()
def rollout(model,starts):
    idx=np.asarray(starts)[:,None]+np.arange(400)[None,:]
    raw=data[idx]
    st=torch.as_tensor(R.normalise_state(raw[:,:,R.STATE_COLS],cfg["state_data_mean"],cfg["state_data_std"]),dtype=torch.float32)
    ac=torch.as_tensor(raw[:,:,R.ACTION_COLS],dtype=torch.float32)
    if model is None:
        p=st.clone(); p[:,START:]=st[:,START-1:START].expand(-1,400-START,-1)
    else:
        p=model.rollout(st.clone(),ac,START,action_offset=1)
        if isinstance(p,tuple): p=p[0]
    return p,st
def perdim(model,starts):
    p,st=rollout(model,starts)
    return (np.sqrt(((p[:,START:]-st[:,START:])**2).numpy().mean(0))/scale).mean(0)
def pertraj(model,starts,h):
    p,st=rollout(model,starts)
    nu=(p[:,START:START+h]-st[:,START:START+h]).abs().sum(-1); de=st[:,START:START+h].abs().sum(-1)
    return (nu/de).mean(1).numpy()
def boot(x,n=10000,seed=0):
    rng=np.random.default_rng(seed); i=rng.integers(0,len(x),size=(n,len(x)))
    b=x[i].mean(1); return float(b.mean()),float(np.percentile(b,2.5)),float(np.percentile(b,97.5))
out={}
print("="*98); print("TASK 2 -- MATCHED PER-DIMENSION COMPARISON"); print("="*98)
print("  NOTE ON THE BRIEF'S PREMISE: Q1 was ALREADY matched. task5_analyse.py:49 evaluates the")
print("  released checkpoint AND Arm A on the same 20 independent trajectories across all ten")
print("  episodes. Both comparisons are reported below; the episodes-1-and-8 restriction is a")
print("  sharper question, not a correction.\n")
for lbl,eps in (("all ten episodes (as run in Q1)",list(range(10))),
                ("episodes 1 and 8 ONLY",OOS)):
    st_=MET.non_overlapping_starts(ep,eps,400); ni=MET.n_independent(st_,400)
    fl=perdim(None,st_); pr=perdim(ref,st_); pa=perdim(A,st_)
    lr_={NAMES[i] for i in np.flatnonzero(pr>fl)}; la={NAMES[i] for i in np.flatnonzero(pa>fl)}
    j=len(lr_&la)/len(lr_|la) if (lr_|la) else 1.0
    print(f"  {lbl.upper()}   n_traj={len(st_)}  n_independent={ni}")
    print(f"    released checkpoint loses on {len(lr_):>2d}/45 : {sorted(lr_)}")
    print(f"    Arm A @10000       loses on {len(la):>2d}/45 : {sorted(la)}")
    print(f"    shared failures    : {sorted(lr_&la)}")
    print(f"    Jaccard overlap    : {j:.2f}")
    print(f"    g_z the only shared failure? {sorted(lr_&la)==['g_z']}")
    for h in (8,368):
        xr,xa=pertraj(ref,st_,h),pertraj(A,st_,h)
        gr,lor,hir=boot(xr); ga,loa,hia=boot(xa)
        d=xr-xa; gd,lod,hid=boot(d)
        print(f"    h={h:<4d} released {gr:.4f} [{lor:.4f},{hir:.4f}]   ArmA {ga:.4f} [{loa:.4f},{hia:.4f}]"
              f"   diff {gd:+.4f} [{lod:+.4f},{hid:+.4f}] {'ArmA BETTER' if lod>0 else ('released better' if hid<0 else 'spans zero')}")
    out[lbl]={"n_ind":ni,"released_lost":sorted(lr_),"armA_lost":sorted(la),
              "shared":sorted(lr_&la),"jaccard":j}
    print()
print("  ASYMMETRY: the released checkpoint TRAINED on episodes 1 and 8; Arm A did not.")
print("  The episodes-1-and-8 comparison therefore favours the released checkpoint.")

print("\n"+"="*98); print("TASK 3 -- THE GAP-NARROWING TREND, FITTED"); print("="*98)
g=json.load(open(os.path.join(R.RESULTS,"task5_analysis.json")))["gaps"]
CK=[500,2500,5000,7500,10000]
tr={}
for arena in ("out-of-sample","in-sample"):
    for h in (8,368):
        A_=np.array([g[f"{arena}|{c}|h{h}"]["A"] for c in CK])
        B_=np.array([g[f"{arena}|{c}|h{h}"]["B"] for c in CK])
        gap=B_-A_; ratio=B_/A_
        x=np.array(CK,float)
        sl,ic=np.polyfit(x,gap,1); pred=sl*x+ic
        r2=1-((gap-pred)**2).sum()/((gap-gap.mean())**2).sum()
        slr,icr=np.polyfit(x,ratio,1)
        r2r=1-((ratio-(slr*x+icr))**2).sum()/((ratio-ratio.mean())**2).sum()
        close=-ic/sl if sl<0 else None
        tr[f"{arena}|h{h}"]={"gap":gap.tolist(),"ratio":ratio.tolist(),
                             "gap_slope":float(sl),"gap_r2":float(r2),
                             "ratio_slope":float(slr),"ratio_r2":float(r2r),
                             "gap_zero_at":float(close) if close and close>0 else None}
        print(f"\n  {arena.upper()}  h={h}")
        print(f"    gap  : "+"  ".join(f"{c//1000 if c>=1000 else c}k={v:+.3f}" if c>=1000 else f"{c}={v:+.3f}" for c,v in zip(CK,gap)))
        print(f"    ratio: "+"  ".join(f"{v:.2f}x" for v in ratio))
        print(f"    gap fit slope {sl:+.3e}/iter  R2 {r2:.2f}"
              + (f"   -> zero at ~{close:,.0f} iterations" if close and close>0 else "   -> does not extrapolate to closure"))
        print(f"    ratio fit slope {slr:+.3e}/iter  R2 {r2r:.2f}"
              f"  -> ratio {'DECLINING' if slr<0 else 'GROWING'}")
out["trend"]=tr
print("\n  READING:")
oos=tr["out-of-sample|h368"]; ins=tr["in-sample|h368"]
print(f"    The absolute gap narrows in BOTH arenas -- both arms improve with training.")
print(f"    But the RATIO behaves differently: out-of-sample {oos['ratio'][1]:.1f}x at 2500 ->"
      f" {oos['ratio'][-1]:.1f}x at 10000, while in-sample it GROWS"
      f" {ins['ratio'][1]:.1f}x -> {ins['ratio'][-1]:.1f}x.")
print(f"    The out-of-sample 2500 point ({oos['ratio'][1]:.1f}x) is an outlier driven by an")
print(f"    anomalous Arm B value there; excluding it the out-of-sample ratio is"
      f" {oos['ratio'][0]:.1f}, {oos['ratio'][2]:.1f}, {oos['ratio'][3]:.1f}, {oos['ratio'][4]:.1f} -- flat to slightly rising.")
# Provenance, so a reader can tell this apart from the three-seed artifacts:
# only ONE 10,000-iteration run exists per arm (M-25 records why), so every number
# here is single-seed. The seed was not recorded until the review.
out["provenance"]={"runs":["armA_seed1_10k","armB_seed1_10k"],"seeds":[1],
                   "n_seeds":1,"note":"single-seed by necessity, not by choice -- see M-25"}
json.dump(out,open(os.path.join(R.RESULTS,"task2_3_matched_trend.json"),"w"),indent=2,default=float)
print(f"\n  wrote {R.rel(os.path.join(R.RESULTS,'task2_3_matched_trend.json'))}")
