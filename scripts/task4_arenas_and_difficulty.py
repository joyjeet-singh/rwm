"""
Task 4a -- re-evaluate all six checkpoints in TWO ARENAS, never one aggregate (M-21).
Task 4b -- does episode difficulty determine the A/B verdict? Rule pre-registered in M-22.

Form 1 pooled aggregation (M-19), independent trajectories only (M-20), n_independent printed
with every figure.
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np, torch
import rwm_data as R, rollout_eval as E, rwm_metrics as MET, rwm_model as M

START = E.START_STEP
ARMS, SEEDS, CKPTS = ("A", "B"), (0, 1, 2), (500, 2500)
NAMES = (["v_x","v_y","v_z","w_x","w_y","w_z","g_x","g_y","g_z"]
         + [f"q_{l}_{a}" for a in ("HAA","HFE","KFE") for l in ("LF","LH","RF","RH")]
         + [f"qd_{l}_{a}" for a in ("HAA","HFE","KFE") for l in ("LF","LH","RF","RH")]
         + [f"tau_{l}_{a}" for a in ("HAA","HFE","KFE") for l in ("LF","LH","RF","RH")])

paths=R.repo_paths(); cfg=R.load_reference_config(paths["lite"])
data,ep=R.load_data(paths["csv"],verbose=False)
split=E.make_split(seed=0,strat_path=os.path.join(R.RESULTS,"step0_strat.json"),verbose=False)
scale=MET.training_scale(data,ep,split["train_episodes"],cfg["state_data_mean"],cfg["state_data_std"])
OOS=list(split["holdout_episodes"]); INS=list(split["train_episodes"])
MODELS={}
for a in ARMS:
    for s in SEEDS:
        for c in CKPTS:
            m=M.build_from_config(cfg,ensemble_size=1)
            m.load_state_dict(torch.load(f"runs/arm{a}_seed{s}/weights_{c}.pt",
                                         map_location="cpu")["model_state_dict"],strict=True)
            m.eval(); MODELS[(a,s,c)]=m

def evaluate(model, starts, L):
    idx=np.asarray(starts)[:,None]+np.arange(L)[None,:]
    raw=data[idx]
    st=torch.as_tensor(R.normalise_state(raw[:,:,R.STATE_COLS],cfg["state_data_mean"],
                                         cfg["state_data_std"]),dtype=torch.float32)
    ac=torch.as_tensor(raw[:,:,R.ACTION_COLS],dtype=torch.float32)
    pr=model.rollout(st.clone(),ac,START,action_offset=1) if model is not None else None
    hd=st.clone(); hd[:,START:]=st[:,START-1:START].expand(-1,L-START,-1)
    p = hd if pr is None else pr
    def l1(h):
        nu=(p[:,START:START+h]-st[:,START:START+h]).abs().sum(-1)
        de=st[:,START:START+h].abs().sum(-1)
        return float((nu/de).mean())
    sq=((p[:,START:]-st[:,START:])**2).numpy()
    return {"l1":{h:l1(h) for h in (8,)|({368} if L==400 else {168})},
            "sq":sq}

def agg(model, starts, L, hs):
    idx=np.asarray(starts)[:,None]+np.arange(L)[None,:]
    raw=data[idx]
    st=torch.as_tensor(R.normalise_state(raw[:,:,R.STATE_COLS],cfg["state_data_mean"],
                                         cfg["state_data_std"]),dtype=torch.float32)
    ac=torch.as_tensor(raw[:,:,R.ACTION_COLS],dtype=torch.float32)
    if model is None:
        p=st.clone(); p[:,START:]=st[:,START-1:START].expand(-1,L-START,-1)
    else:
        p=model.rollout(st.clone(),ac,START,action_offset=1)
    out={}
    for h in hs:
        nu=(p[:,START:START+h]-st[:,START:START+h]).abs().sum(-1)
        de=st[:,START:START+h].abs().sum(-1)
        sq=((p[:,START:START+h]-st[:,START:START+h])**2).numpy()
        out[h]={"l1":float((nu/de).mean()),"nrmse":MET.nrmse_pooled(sq,scale)}
    return out

out={}
print("="*98); print("TASK 4a -- TWO ARENAS, FOUR TABLES  (form 1 pooled, independent trajectories)"); print("="*98)
tables={}
for arena,eps in (("out-of-sample",OOS),("in-sample",INS)):
    for L,hs in ((400,(8,368)),(200,(8,168))):
        st_=MET.non_overlapping_starts(ep,eps,L)
        ni=MET.n_independent(st_,L)
        key=f"{arena}@{L}"
        print(f"\n  {arena.upper()}  episodes {eps}  |  {L}-step  |  "
              f"n_trajectories={len(st_)}  n_independent={ni}"
              + ("   <-- CAVEAT: n_independent below 10" if ni<10 else ""))
        rows={}
        fl=agg(None,st_,L,hs)
        hdr=f"    {'run':<12s} " + " ".join(f"{'h='+str(h)+' l1':>10s} {'h='+str(h)+' nR':>10s}" for h in hs)
        print(hdr)
        for a in ARMS:
            for s in SEEDS:
                for c in CKPTS:
                    r=agg(MODELS[(a,s,c)],st_,L,hs); rows[f"{a}{s}@{c}"]=r
        for c in CKPTS:
            for a in ARMS:
                v={h:{k:np.array([rows[f'{a}{s}@{c}'][h][k] for s in SEEDS]) for k in ("l1","nrmse")} for h in hs}
                line=f"    arm{a} @{c:<6d}"
                for h in hs:
                    line+=f" {v[h]['l1'].mean():>6.4f}±{v[h]['l1'].std(ddof=1):<4.3f}"
                    line+=f" {v[h]['nrmse'].mean():>6.4f}±{v[h]['nrmse'].std(ddof=1):<4.3f}"
                print(line)
        print(f"    {'floor':<12s}"+"".join(f" {fl[h]['l1']:>6.4f}{'':<5s} {fl[h]['nrmse']:>6.4f}{'':<5s}" for h in hs))
        tables[key]={"episodes":eps,"len":L,"n_traj":len(st_),"n_independent":ni,
                     "rows":{k:{str(h):v for h,v in r.items()} for k,r in rows.items()},
                     "floor":{str(h):v for h,v in fl.items()}}
out["task4a"]=tables

print("\n"+"="*98); print("  M-16 RE-EVALUATED IN BOTH ARENAS (h=8, ddof=1)"); print("="*98)
m16={}
for arena in ("out-of-sample","in-sample"):
    for L in (400,200):
        t=tables[f"{arena}@{L}"]
        for metric in ("l1","nrmse"):
            g=lambda a,c: np.array([t["rows"][f"{a}{s}@{c}"]["8"][metric] for s in SEEDS])
            A5,B5,A25,B25=g("A",500),g("B",500),g("A",2500),g("B",2500)
            l5="A" if A5.mean()<B5.mean() else "B"; l25="A" if A25.mean()<B25.mean() else "B"
            d=abs(A25.mean()-B25.mean()); sp=max(A25.std(ddof=1),B25.std(ddof=1))
            v="settled" if (l5==l25 and d>sp) else "cannot be settled at this budget"
            m16[f"{arena}@{L}|{metric}"]={"leader_500":l5,"leader_2500":l25,"same":l5==l25,
                                          "diff":float(d),"spread":float(sp),"verdict":v,
                                          "n_independent":t["n_independent"]}
            print(f"  {arena:<14s} {L}-step {metric:>6s}: @500 {l5} @2500 {l25} same={str(l5==l25):<5s}"
                  f" |A-B| {d:.4f} vs sd {sp:.4f}  -> {v.upper()}  (n_ind={t['n_independent']})")
allv={k:v["verdict"] for k,v in m16.items()}
agree=len(set(allv.values()))==1
print(f"\n  all eight arena/length/metric combinations agree: {agree}")
if not agree:
    print("  *** ARENAS DISAGREE -- this outranks everything else ***")
    for k,v in allv.items(): print(f"      {k}: {v}")
out["m16_arenas"]=m16; out["m16_all_agree"]=bool(agree)

# ================================================================= TASK 4b
print("\n"+"="*98); print("TASK 4b -- DOES EPISODE DIFFICULTY DETERMINE THE VERDICT?"); print("="*98)
diff=json.load(open(os.path.join(R.RESULTS,"step4_0a_results.json")))["per_episode_e"]["1"]
diff={int(k):v for k,v in diff.items()}
per_ep={}
print(f"  {'ep':>3s} {'difficulty':>10s} {'n@400':>6s} | {'gapA-B h=8':>11s} {'gap h=368':>10s}"
      f" | {'gap h=8 nR':>11s} {'gap h=368 nR':>13s}  arena")
for e_ in range(10):
    s400=MET.non_overlapping_starts(ep,[e_],400)
    g={}
    for h,metric in ((8,"l1"),(368,"l1"),(8,"nrmse"),(368,"nrmse")):
        A=np.mean([agg(MODELS[("A",s,2500)],s400,400,(h,))[h][metric] for s in SEEDS])
        B=np.mean([agg(MODELS[("B",s,2500)],s400,400,(h,))[h][metric] for s in SEEDS])
        g[f"{metric}{h}"]=float(B-A)          # positive = A better (lower error)
    per_ep[e_]={"difficulty":diff[e_],"n":len(s400),**g}
    print(f"  {e_:>3d} {diff[e_]:>10.4f} {len(s400):>6d} | {g['l18']:>+11.4f} {g['l1368']:>+10.4f}"
          f" | {g['nrmse8']:>+11.4f} {g['nrmse368']:>+13.4f}  {'HELD OUT' if e_ in OOS else ''}")
print("\n  (gap = ArmB - ArmA, so POSITIVE means Arm A is better)")
res={}
for k,lbl in (("l18","relative-L1 h=8"),("l1368","relative-L1 h=368"),
              ("nrmse8","nRMSE h=8"),("nrmse368","nRMSE h=368")):
    d_=np.array([per_ep[e]["difficulty"] for e in range(10)])
    g_=np.array([per_ep[e][k] for e in range(10)])
    r=float(np.corrcoef(d_,g_)[0,1])
    bs=np.random.default_rng(0).integers(0,10,size=(10000,10))
    rb=np.array([np.corrcoef(d_[b],g_[b])[0,1] for b in bs])
    lo,hi=np.percentile(rb[~np.isnan(rb)],[2.5,97.5])
    signs=set(np.sign(g_).astype(int).tolist())
    ho=np.mean([per_ep[e][k] for e in OOS]); other=np.mean([per_ep[e][k] for e in INS])
    res[k]={"r":r,"ci":[float(lo),float(hi)],"sign_consistent":len(signs)==1,
            "signs":sorted(signs),"gap_holdout":float(ho),"gap_other":float(other)}
    print(f"\n  {lbl}")
    print(f"    correlation gap vs difficulty: r = {r:+.3f}   95% CI [{lo:+.3f}, {hi:+.3f}]"
          f"   {'spans zero' if lo<0<hi else 'excludes zero'}")
    print(f"    gap on held-out pair {ho:+.4f}   on the other eight {other:+.4f}"
          f"   ({'held-out UNDERstates' if ho<other else 'held-out OVERstates'} by {abs(other-ho):.4f})")
    print(f"    sign consistent across all ten episodes: {len(signs)==1}"
          f"  (signs present: {sorted(signs)})")
out["task4b"]={"per_episode":per_ep,"correlations":res}

print("\n"+"="*98); print("  M-22's PRE-REGISTERED RULE, APPLIED"); print("="*98)
key="l18"; r=res[key]["r"]; lo,hi=res[key]["ci"]
weak = abs(r)<0.4 or (lo<0<hi)
if weak: branch="1 -- WEAK: the held-out pair's easiness does not bias the comparison. M-16 stands as measured; no retraining warranted; Task 4c does NOT run."
elif r>0: branch="2 -- GAP GROWS WITH DIFFICULTY: the out-of-sample estimate is CONSERVATIVE. Finding strengthens; Task 4c does NOT run."
else: branch="3 -- GAP SHRINKS WITH DIFFICULTY: the easy held-out pair inflates the result. Task 4c (cross-validation) MUST run."
print(f"  governing metric: relative-L1 at h=8 (where M-16 was pre-registered)")
print(f"  r = {r:+.3f}, CI [{lo:+.3f}, {hi:+.3f}]  ->  BRANCH {branch}")
allsign=all(res[k]["sign_consistent"] for k in res)
print(f"\n  sign of the gap consistent across all ten episodes, on every metric: {allsign}")
if not allsign:
    print("  *** THE GAP REVERSES SIGN ON AT LEAST ONE EPISODE -- outranks the correlation ***")
    for k in res:
        if not res[k]["sign_consistent"]:
            bad=[e for e in range(10) if per_ep[e][k]<0]
            print(f"      {k}: negative on episodes {bad}")
out["rule_branch"]=branch; out["sign_consistent_all"]=bool(allsign)
json.dump(out,open(os.path.join(R.RESULTS,"task4_arenas.json"),"w"),indent=2,default=float)
print(f"\n  wrote {R.rel(os.path.join(R.RESULTS,'task4_arenas.json'))}")
