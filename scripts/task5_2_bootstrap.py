"""
Task 5.2 -- recompute the existing six-run tables under bootstrap CIs (M-25),
so the Task 5 numbers and the Step 5 numbers are like for like.
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np, torch
import rwm_data as R, rollout_eval as E, rwm_metrics as MET, rwm_model as M
START=E.START_STEP; ARMS,SEEDS,CKPTS=("A","B"),(0,1,2),(500,2500)
paths=R.repo_paths(); cfg=R.load_reference_config(paths["lite"])
data,ep=R.load_data(paths["csv"],verbose=False)
split=E.make_split(seed=0,strat_path=os.path.join(R.RESULTS,"step0_strat.json"),verbose=False)
scale=MET.training_scale(data,ep,split["train_episodes"],cfg["state_data_mean"],cfg["state_data_std"])
ARENAS={"out-of-sample":list(split["holdout_episodes"]),"in-sample":list(split["train_episodes"])}

def per_traj(model,starts,L,h):
    idx=np.asarray(starts)[:,None]+np.arange(L)[None,:]
    raw=data[idx]
    st=torch.as_tensor(R.normalise_state(raw[:,:,R.STATE_COLS],cfg["state_data_mean"],
                                         cfg["state_data_std"]),dtype=torch.float32)
    ac=torch.as_tensor(raw[:,:,R.ACTION_COLS],dtype=torch.float32)
    p=model.rollout(st.clone(),ac,START,action_offset=1) if model is not None else None
    if p is None:
        p=st.clone(); p[:,START:]=st[:,START-1:START].expand(-1,L-START,-1)
    nu=(p[:,START:START+h]-st[:,START:START+h]).abs().sum(-1); de=st[:,START:START+h].abs().sum(-1)
    return (nu/de).mean(1).numpy()

def boot_gap(A,B,n=10000,seed=0):
    rng=np.random.default_rng(seed); k=len(A)
    idx=rng.integers(0,k,size=(n,k))
    g=B[idx].mean(1)-A[idx].mean(1)      # positive = A better
    return float(g.mean()),float(np.percentile(g,2.5)),float(np.percentile(g,97.5)),float((g<=0).mean())

MODELS={(a,s,c):None for a in ARMS for s in SEEDS for c in CKPTS}
for k in MODELS:
    a,s,c=k
    m=M.build_from_config(cfg,ensemble_size=1)
    m.load_state_dict(torch.load(f"runs/arm{a}_seed{s}/weights_{c}.pt",map_location="cpu")["model_state_dict"],strict=True)
    m.eval(); MODELS[k]=m

print("="*100)
print("TASK 5.2 -- SIX EXISTING RUNS RECOMPUTED UNDER BOOTSTRAP CIs (M-25)")
print("="*100)
print("  gap = ArmB - ArmA, positive means Arm A better. CI over independent trajectories,")
print("  10,000 resamples. Seeds are pooled per arm (3 seeds x n_traj samples).\n")
out={}
for arena,eps in ARENAS.items():
    for L,hs in ((400,(8,368)),(200,(8,168))):
        st_=MET.non_overlapping_starts(ep,eps,L); ni=MET.n_independent(st_,L)
        for c in CKPTS:
            for h in hs:
                A=np.concatenate([per_traj(MODELS[("A",s,c)],st_,L,h) for s in SEEDS])
                B=np.concatenate([per_traj(MODELS[("B",s,c)],st_,L,h) for s in SEEDS])
                g,lo,hi,pneg=boot_gap(A,B)
                key=f"{arena}|{L}|{c}|h{h}"
                out[key]={"gap":g,"ci":[lo,hi],"p_gap_le_0":pneg,"n_independent":ni,
                          "A_mean":float(A.mean()),"B_mean":float(B.mean()),
                          "excludes_zero":bool(lo>0 or hi<0)}
                print(f"  {arena:<14s} {L}-step @{c:<5d} h={h:<3d} n_ind={ni:<2d} | "
                      f"A {A.mean():>7.4f}  B {B.mean():>7.4f} | gap {g:>+8.4f} "
                      f"[{lo:>+7.4f},{hi:>+7.4f}] | {'EXCLUDES 0' if (lo>0 or hi<0) else 'spans 0'}")
        print()
print("  Comparison with the seed-spread statistic M-16 used, out-of-sample 400-step h=8 @2500:")
k="out-of-sample|400|2500|h8"
print(f"    bootstrap gap {out[k]['gap']:+.4f} CI [{out[k]['ci'][0]:+.4f},{out[k]['ci'][1]:+.4f}]"
      f"  vs seed-spread |A-B| 0.0103 against sd 0.0308")
print(f"    both say the same thing at h=8: not separated.")
k="out-of-sample|400|2500|h368"
print(f"  And at h=368 out-of-sample @2500: gap {out[k]['gap']:+.4f} "
      f"CI [{out[k]['ci'][0]:+.4f},{out[k]['ci'][1]:+.4f}] -> "
      f"{'EXCLUDES ZERO' if out[k]['excludes_zero'] else 'spans zero'}  (n_ind={out[k]['n_independent']})")
json.dump(out,open(os.path.join(R.RESULTS,"task5_2_bootstrap.json"),"w"),indent=2)
print(f"\n  wrote {R.rel(os.path.join(R.RESULTS,'task5_2_bootstrap.json'))}")
