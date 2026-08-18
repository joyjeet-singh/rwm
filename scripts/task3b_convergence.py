"""Is the Task 2 flip real, or an artifact? Convergence of both metrics in n_trajectories."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np, torch
import rwm_data as R, rollout_eval as E, rwm_metrics as MET, score_reference as S

paths=R.repo_paths(); cfg=R.load_reference_config(paths["lite"])
data,ep=R.load_data(paths["csv"],verbose=False)
split=E.make_split(seed=0,strat_path=os.path.join(R.RESULTS,"step0_strat.json"),verbose=False)
scale=MET.training_scale(data,ep,split["train_episodes"],cfg["state_data_mean"],cfg["state_data_std"])
ref=S.ReferenceRWM(torch.load(paths["ckpt"],map_location="cpu")["system_dynamics_state_dict"])

def ev(n,seed):
    idx=E.sample_trajectories(ep,split["holdout_episodes"],n_traj=n,len_traj=400,seed=seed)
    raw=data[idx]
    st=torch.as_tensor(R.normalise_state(raw[:,:,R.STATE_COLS],cfg["state_data_mean"],cfg["state_data_std"]),dtype=torch.float32)
    ac=torch.as_tensor(raw[:,:,R.ACTION_COLS],dtype=torch.float32)
    pred,*_=ref.rollout(st.clone(),ac,E.START_STEP,action_offset=1)
    hold=st.clone(); hold[:,E.START_STEP:]=st[:,E.START_STEP-1:E.START_STEP].expand(-1,400-E.START_STEP,-1)
    def l1(p):
        nu=(p[:,E.START_STEP:]-st[:,E.START_STEP:]).abs().sum(-1); de=st[:,E.START_STEP:].abs().sum(-1)
        return float((nu/de).mean())
    nm,_=MET.nrmse_per_step(pred,st,scale,E.START_STEP); nf,_=MET.nrmse_per_step(hold,st,scale,E.START_STEP)
    return l1(pred),l1(hold),float(nm.mean()),float(nf.mean())

print("="*94)
print("TASK 3b -- IS THE FLIP REAL? convergence of both metrics in n_trajectories (h=368)")
print("="*94)
print(f"  {'n':>5s} {'seeds':>6s} | {'e model':>16s} {'e floor':>16s} {'beats?':>7s} | {'nRMSE model':>17s} {'nRMSE floor':>17s} {'beats?':>7s}")
rows={}
for n in (10,25,50,100,200,400):
    S_=8 if n<=100 else 4
    r=np.array([ev(n,s) for s in range(S_)])
    em,ef,nm,nf=r[:,0],r[:,1],r[:,2],r[:,3]
    be=(em<ef).mean(); bn=(nm<nf).mean()
    rows[n]={"e_model":[float(em.mean()),float(em.std(ddof=1))],"e_floor":[float(ef.mean()),float(ef.std(ddof=1))],
             "nrmse_model":[float(nm.mean()),float(nm.std(ddof=1))],"nrmse_floor":[float(nf.mean()),float(nf.std(ddof=1))],
             "frac_beats_e":float(be),"frac_beats_nrmse":float(bn),"n_seeds":S_}
    print(f"  {n:>5d} {S_:>6d} | {em.mean():>8.4f}+-{em.std(ddof=1):<7.4f} {ef.mean():>8.4f}+-{ef.std(ddof=1):<7.4f}"
          f" {be:>6.0%} | {nm.mean():>9.4f}+-{nm.std(ddof=1):<7.4f} {nf.mean():>9.4f}+-{nf.std(ddof=1):<7.4f} {bn:>6.0%}")
print()
print("  Reading: relative-L1 is stable in n; nRMSE rises with n because RMSE across")
print("  trajectories is a TAIL statistic -- a small sample misses the worst trajectories,")
print("  so small-n nRMSE is biased LOW, not merely noisy.")
json.dump(rows,open(os.path.join(R.RESULTS,"task3b_convergence.json"),"w"),indent=2)
print(f"\n  wrote {R.rel(os.path.join(R.RESULTS,'task3b_convergence.json'))}")
