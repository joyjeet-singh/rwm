"""
Task 5 analysis -- M-23's verdict and the four questions, in order of value.

M-23 governing measurement: relative-L1 at h=368, out-of-sample arena, 400-step,
form 1 pooled, 95% bootstrap CI over independent trajectories.
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np, torch
import rwm_data as R, rollout_eval as E, rwm_metrics as MET, rwm_model as M, score_reference as S

START=E.START_STEP; CK=(500,2500,5000,7500,10000)
NAMES=(["v_x","v_y","v_z","w_x","w_y","w_z","g_x","g_y","g_z"]
       +[f"q_{l}_{a}" for a in ("HAA","HFE","KFE") for l in ("LF","LH","RF","RH")]
       +[f"qd_{l}_{a}" for a in ("HAA","HFE","KFE") for l in ("LF","LH","RF","RH")]
       +[f"tau_{l}_{a}" for a in ("HAA","HFE","KFE") for l in ("LF","LH","RF","RH")])
REF7={'v_z','w_x','w_y','g_x','g_y','g_z','tau_RF_HAA'}
paths=R.repo_paths(); cfg=R.load_reference_config(paths["lite"])
data,ep=R.load_data(paths["csv"],verbose=False)
split=E.make_split(seed=0,strat_path=os.path.join(R.RESULTS,"step0_strat.json"),verbose=False)
scale=MET.training_scale(data,ep,split["train_episodes"],cfg["state_data_mean"],cfg["state_data_std"])
OOS=list(split["holdout_episodes"]); INS=list(split["train_episodes"])
def load(a,c):
    m=M.build_from_config(cfg,ensemble_size=1)
    m.load_state_dict(torch.load(f"runs/arm{a}_seed1_10k/weights_{c}.pt",map_location="cpu")["model_state_dict"],strict=True)
    m.eval(); return m
def traj(model,starts,L,h,metric):
    idx=np.asarray(starts)[:,None]+np.arange(L)[None,:]
    raw=data[idx]
    st=torch.as_tensor(R.normalise_state(raw[:,:,R.STATE_COLS],cfg["state_data_mean"],cfg["state_data_std"]),dtype=torch.float32)
    ac=torch.as_tensor(raw[:,:,R.ACTION_COLS],dtype=torch.float32)
    p=model.rollout(st.clone(),ac,START,action_offset=1) if model else None
    if p is None: p=st.clone(); p[:,START:]=st[:,START-1:START].expand(-1,L-START,-1)
    if metric=="l1":
        nu=(p[:,START:START+h]-st[:,START:START+h]).abs().sum(-1); de=st[:,START:START+h].abs().sum(-1)
        return (nu/de).mean(1).numpy()
    sq=((p[:,START:START+h]-st[:,START:START+h])**2).numpy()
    return np.array([MET.nrmse_pooled(sq[i:i+1],scale) for i in range(len(sq))])
def boot(A,B,n=10000,seed=0):
    rng=np.random.default_rng(seed); k=len(A); i=rng.integers(0,k,size=(n,k))
    g=B[i].mean(1)-A[i].mean(1)
    return float(g.mean()),float(np.percentile(g,2.5)),float(np.percentile(g,97.5))
out={}
print("="*100); print("TASK 5 -- 10,000-ITERATION CONVERGENCE RUNS"); print("="*100)

# ---------------- Q1 per-dimension pattern
print("\n"+"="*100); print("Q1 -- DOES A FROM-SCRATCH MODEL DEVELOP THE RELEASED CHECKPOINT'S FAILURE PATTERN?"); print("="*100)
print(f"  released checkpoint loses on 7 of 45: {sorted(REF7)}\n")
allst=MET.non_overlapping_starts(ep,range(10),400)
def perdim(model,starts):
    idx=np.asarray(starts)[:,None]+np.arange(400)[None,:]
    raw=data[idx]
    st=torch.as_tensor(R.normalise_state(raw[:,:,R.STATE_COLS],cfg["state_data_mean"],cfg["state_data_std"]),dtype=torch.float32)
    ac=torch.as_tensor(raw[:,:,R.ACTION_COLS],dtype=torch.float32)
    p=model.rollout(st.clone(),ac,START,action_offset=1) if model else None
    if p is None: p=st.clone(); p[:,START:]=st[:,START-1:START].expand(-1,400-START,-1)
    return (np.sqrt(((p[:,START:]-st[:,START:])**2).numpy().mean(0))/scale).mean(0)
fl=perdim(None,allst)
q1={}
print(f"  {'run':<16s} {'lost':>5s}  overlap with the released 7   dims lost")
for a in ("A","B"):
    for c in CK:
        pdm=perdim(load(a,c),allst); lost={NAMES[i] for i in np.flatnonzero(pdm>fl)}
        ov=lost&REF7
        q1[f"{a}@{c}"]={"n_lost":len(lost),"lost":sorted(lost),"overlap":sorted(ov),
                        "overlap_frac":len(ov)/7}
        print(f"  arm{a} @{c:<7d} {len(lost):>5d}  {len(ov)}/7 = {len(ov)/7:>4.0%}   {sorted(lost)}")
out["q1"]=q1
a10=set(q1["A@10000"]["lost"]); print(f"\n  Arm A @10000 lost-set vs released 7:")
print(f"    shared    : {sorted(a10&REF7)}")
print(f"    only ArmA : {sorted(a10-REF7)}")
print(f"    only ref  : {sorted(REF7-a10)}")
j=len(a10&REF7)/len(a10|REF7); print(f"    Jaccard   : {j:.2f}")
out["q1_jaccard_A10000"]=j

# ---------------- Q2/Q3 gaps with CIs
print("\n"+"="*100); print("Q2 & Q3 -- THE A/B GAP AT h=8 AND h=368, ALL CHECKPOINTS, BOTH ARENAS"); print("="*100)
gaps={}
for arena,eps in (("out-of-sample",OOS),("in-sample",INS)):
    st_=MET.non_overlapping_starts(ep,eps,400); ni=MET.n_independent(st_,400)
    print(f"\n  {arena.upper()}  n_independent={ni}")
    print(f"    {'ckpt':>6s} | {'h=8 A':>7s} {'h=8 B':>7s} {'gap':>8s} {'95% CI':>20s} {'excl 0':>7s}"
          f" | {'h=368 A':>8s} {'h=368 B':>8s} {'gap':>8s} {'95% CI':>20s} {'excl 0':>7s}")
    for c in CK:
        row=f"    {c:>6d} |"
        for h in (8,368):
            A=traj(load("A",c),st_,400,h,"l1"); B=traj(load("B",c),st_,400,h,"l1")
            g,lo,hi=boot(A,B); ex=(lo>0 or hi<0)
            gaps[f"{arena}|{c}|h{h}"]={"A":float(A.mean()),"B":float(B.mean()),"gap":g,
                                       "ci":[lo,hi],"excludes_zero":bool(ex),"n_ind":ni}
            row+=f" {A.mean():>7.4f} {B.mean():>7.4f} {g:>+8.4f} [{lo:>+7.3f},{hi:>+7.3f}] {'YES' if ex else 'no':>7s} |"
        print(row)
out["gaps"]=gaps

# ---------------- per-episode sign
print("\n"+"="*100); print("  PER-EPISODE SIGN OF THE GAP AT 10,000 (M-23 condition 3)"); print("="*100)
mA,mB=load("A",10000),load("B",10000)
sign={}
print(f"  {'ep':>3s} {'gap h=8':>10s} {'gap h=368':>11s}  arena")
for e_ in range(10):
    s4=MET.non_overlapping_starts(ep,[e_],400)
    g8=float(traj(mB,s4,400,8,"l1").mean()-traj(mA,s4,400,8,"l1").mean())
    g368=float(traj(mB,s4,400,368,"l1").mean()-traj(mA,s4,400,368,"l1").mean())
    sign[e_]={"h8":g8,"h368":g368}
    print(f"  {e_:>3d} {g8:>+10.4f} {g368:>+11.4f}  {'HELD OUT' if e_ in OOS else ''}")
s368=[sign[e]["h368"] for e in range(10)]; s8=[sign[e]["h8"] for e in range(10)]
c368=all(x>0 for x in s368); c8=all(x>0 for x in s8)
print(f"\n  h=368 positive on all ten: {c368}   (range {min(s368):+.3f} to {max(s368):+.3f})")
print(f"  h=8   positive on all ten: {c8}"+("" if c8 else f"   negative on {[e for e in range(10) if sign[e]['h8']<0]}"))
out["per_episode"]=sign; out["sign_consistent_h368"]=bool(c368); out["sign_consistent_h8"]=bool(c8)

# ---------------- M-23
print("\n"+"="*100); print("  M-23's PRE-REGISTERED RULE, APPLIED"); print("="*100)
g25=gaps["out-of-sample|2500|h368"]; g10=gaps["out-of-sample|10000|h368"]
c1=g25["gap"]>0 and g10["gap"]>0; c2=g10["excludes_zero"] and g10["ci"][0]>0; c3=c368
print(f"  governing: relative-L1, h=368, out-of-sample, 400-step, form1 pooled, bootstrap CI")
print(f"    condition 1  Arm A leads at 2500 and 10000 : {c1}"
      f"   (gaps {g25['gap']:+.4f}, {g10['gap']:+.4f})")
print(f"    condition 2  95% CI excludes zero at 10000 : {c2}"
      f"   (CI [{g10['ci'][0]:+.4f}, {g10['ci'][1]:+.4f}], n_ind={g10['n_ind']})")
print(f"    condition 3  per-episode sign consistent   : {c3}")
v="REPRODUCES AT LONG HORIZON" if (c1 and c2 and c3) else ("FAILS TO REPRODUCE" if not c1 else "CANNOT BE SETTLED")
print(f"\n  VERDICT: {v}")
out["m23"]={"c1":bool(c1),"c2":bool(c2),"c3":bool(c3),"verdict":v}
print("\n  secondaries (reported, not governing):")
sec={}
for lbl,k in (("h=8 out-of-sample","out-of-sample|10000|h8"),
              ("h=368 in-sample","in-sample|10000|h368"),
              ("h=8 in-sample","in-sample|10000|h8")):
    g=gaps[k]; sec[lbl]={"gap":g["gap"],"ci":g["ci"],"excludes_zero":g["excludes_zero"]}
    print(f"    {lbl:<20s} gap {g['gap']:+.4f} CI [{g['ci'][0]:+.4f},{g['ci'][1]:+.4f}]"
          f" -> {'A leads, CI excludes 0' if g['gap']>0 and g['excludes_zero'] else ('spans zero' if not g['excludes_zero'] else 'B leads')}")
out["secondaries"]=sec

# ---------------- Q4 collapse
print("\n"+"="*100); print("Q4 -- DOES THE COLLAPSE RATE STAY LINEAR TO 10,000?"); print("="*100)
q4={}
for a in ("A","B"):
    d=json.load(open(os.path.join(R.RESULTS,f"step5_arm{a}_seed1_10k.json")))
    it=np.array([c["iter"] for c in d["collapse"]],float)
    ld=np.log(np.array([c["exp_log_delta_logstd_mean"] for c in d["collapse"]]))
    sl,_=np.polyfit(it,ld,1)
    e25=float(np.exp(ld[it<=2500][-1])); e10=float(np.exp(ld[-1]))
    pred=float(np.exp(-9.4362e-05*10000))
    q4[a]={"rate_10k":float(sl),"exp_at_10000":e10,"predicted":pred,
           "rate_2500_pooled":-9.4362e-05,"implied_iters":float(-14.4629/sl)}
    print(f"  arm{a}: rate over 10,000 = {sl:.4e} (rate/lr {abs(sl)/1e-4:.2f})")
    print(f"        exp(log_delta) at 10,000 = {e10:.6f}   pre-registered prediction {pred:.4f}"
          f"   error {100*(e10/pred-1):+.1f}%")
    print(f"        implied iterations to -14.4629: {-14.4629/sl:,.0f}"
          f"  (from the 2500-iteration pooled fit: 153,270)")
out["q4"]=q4
json.dump(out,open(os.path.join(R.RESULTS,"task5_analysis.json"),"w"),indent=2,default=float)
print(f"\n  wrote {R.rel(os.path.join(R.RESULTS,'task5_analysis.json'))}")
