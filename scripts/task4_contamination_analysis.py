"""Task 4 -- what the spliced windows actually cost (O-06)."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np, torch
import rwm_data as R, rollout_eval as E, rwm_metrics as MET, rwm_model as M
START=E.START_STEP; SEEDS=(0,1,2); CK=(500,2500)
paths=R.repo_paths(); cfg=R.load_reference_config(paths["lite"])
data,ep=R.load_data(paths["csv"],verbose=False)
split=E.make_split(seed=0,strat_path=os.path.join(R.RESULTS,"step0_strat.json"),verbose=False)
scale=MET.training_scale(data,ep,split["train_episodes"],cfg["state_data_mean"],cfg["state_data_std"])
ARENAS={"out-of-sample":list(split["holdout_episodes"]),"in-sample":list(split["train_episodes"])}
def load(tag,s,c):
    m=M.build_from_config(cfg,ensemble_size=1)
    m.load_state_dict(torch.load(f"runs/armA_seed{s}{tag}/weights_{c}.pt",map_location="cpu")["model_state_dict"],strict=True)
    m.eval(); return m
def pertraj(model,starts,L,h,metric):
    idx=np.asarray(starts)[:,None]+np.arange(L)[None,:]
    raw=data[idx]
    st=torch.as_tensor(R.normalise_state(raw[:,:,R.STATE_COLS],cfg["state_data_mean"],cfg["state_data_std"]),dtype=torch.float32)
    ac=torch.as_tensor(raw[:,:,R.ACTION_COLS],dtype=torch.float32)
    p=model.rollout(st.clone(),ac,START,action_offset=1)
    if metric=="l1":
        nu=(p[:,START:START+h]-st[:,START:START+h]).abs().sum(-1); de=st[:,START:START+h].abs().sum(-1)
        return (nu/de).mean(1).numpy()
    sq=((p[:,START:START+h]-st[:,START:START+h])**2).numpy()
    return np.array([MET.nrmse_pooled(sq[i:i+1],scale) for i in range(len(sq))])
def boot_diff(A,B,n=10000,seed=0):
    rng=np.random.default_rng(seed); k=len(A); i=rng.integers(0,k,size=(n,k))
    d=B[i].mean(1)-A[i].mean(1)
    return float(d.mean()),float(np.percentile(d,2.5)),float(np.percentile(d,97.5))
print("="*100); print("TASK 4 -- THE COST OF THE SPLICED WINDOWS (O-06)"); print("="*100)
print("  clean Arm A (7,687 windows) vs contaminated Arm A (7,882 = 7,687 + 195 splices, 2.47%)")
print("  3 seeds each, 2500 iterations, identical in every other respect.")
print("  diff = contaminated - clean, so POSITIVE means contamination HURT.\n")
out={}
for arena,eps in ARENAS.items():
    for L,hs in ((400,(8,368)),(200,(8,168))):
        st_=MET.non_overlapping_starts(ep,eps,L); ni=MET.n_independent(st_,L)
        print(f"  {arena.upper()}  {L}-step  n_independent={ni}")
        print(f"    {'ckpt':>5s} {'h':>4s} {'metric':>7s} | {'clean':>8s} {'contam':>8s} | {'diff':>9s} {'95% CI':>22s}  verdict")
        for c in CK:
            for h in hs:
                for metric in ("l1","nrmse"):
                    A=np.concatenate([pertraj(load("",s,c),st_,L,h,metric) for s in SEEDS])
                    B=np.concatenate([pertraj(load("_contam",s,c),st_,L,h,metric) for s in SEEDS])
                    d,lo,hi=boot_diff(A,B)
                    sig = lo>0 or hi<0
                    out[f"{arena}|{L}|{c}|h{h}|{metric}"]={"clean":float(A.mean()),"contam":float(B.mean()),
                        "diff":d,"ci":[lo,hi],"significant":bool(sig),"n_ind":ni}
                    print(f"    {c:>5d} {h:>4d} {metric:>7s} | {A.mean():>8.4f} {B.mean():>8.4f} |"
                          f" {d:>+9.4f} [{lo:>+8.4f},{hi:>+8.4f}]  "
                          f"{'CONTAMINATION HURT' if sig and d>0 else ('contamination HELPED' if sig else 'no effect')}")
        print()
sig=[k for k,v in out.items() if v["significant"]]
print("="*100)
print(f"  comparisons run: {len(out)}   with a CI excluding zero: {len(sig)}")
if sig:
    for k in sig: print(f"    {k}: diff {out[k]['diff']:+.4f} CI [{out[k]['ci'][0]:+.4f},{out[k]['ci'][1]:+.4f}]")
else:
    print("    NONE. At 2.47% contamination, 3 seeds, 2500 iterations, the 195 spliced")
    print("    windows have NO MEASURABLE EFFECT on any arena, horizon, metric or checkpoint.")
# training-loss comparison
print("\n  training loss at 2500 (mean over 3 seeds):")
for tag,lbl in (("","clean"),("_contam","contaminated")):
    v=[json.load(open(os.path.join(R.RESULTS,f"step5_armA_seed{s}{tag}.json")))["final_terms"]["state"] for s in SEEDS]
    print(f"    {lbl:<14s} {np.mean(v):.4f} +- {np.std(v,ddof=1):.4f}")
json.dump(out,open(os.path.join(R.RESULTS,"task4_contamination.json"),"w"),indent=2)
print(f"\n  wrote {R.rel(os.path.join(R.RESULTS,'task4_contamination.json'))}")
