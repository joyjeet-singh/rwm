"""
Task A -- the two checks that gate R-27.
Task B -- prove M-17's mechanism is Jensen, and fix the estimator.

One 400-trajectory rollout per evaluation seed; every statistic below is derived from the
stored per-trajectory / per-step / per-dimension squared error, so nothing is re-rolled.
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np, torch
import rwm_data as R, rollout_eval as E, rwm_metrics as MET, score_reference as S

N_BIG, SEEDS, START = 400, range(8), E.START_STEP
NAMES = (["v_x","v_y","v_z","w_x","w_y","w_z","g_x","g_y","g_z"]
         + [f"q_{j}" for j in [f"{l}_{a}" for a in ("HAA","HFE","KFE") for l in ("LF","LH","RF","RH")]]
         + [f"qd_{j}" for j in [f"{l}_{a}" for a in ("HAA","HFE","KFE") for l in ("LF","LH","RF","RH")]]
         + [f"tau_{j}" for j in [f"{l}_{a}" for a in ("HAA","HFE","KFE") for l in ("LF","LH","RF","RH")]])

paths=R.repo_paths(); cfg=R.load_reference_config(paths["lite"])
data,ep=R.load_data(paths["csv"],verbose=False)
split=E.make_split(seed=0,strat_path=os.path.join(R.RESULTS,"step0_strat.json"),verbose=False)
scale=MET.training_scale(data,ep,split["train_episodes"],cfg["state_data_mean"],cfg["state_data_std"])
ref=S.ReferenceRWM(torch.load(paths["ckpt"],map_location="cpu")["system_dynamics_state_dict"])

def sq_err(seed,n=N_BIG):
    """Returns (sq_model, sq_floor, start_rows, episodes); sq is (n, T', 45) squared error."""
    idx=E.sample_trajectories(ep,split["holdout_episodes"],n_traj=n,len_traj=400,seed=seed)
    raw=data[idx]
    st=torch.as_tensor(R.normalise_state(raw[:,:,R.STATE_COLS],cfg["state_data_mean"],cfg["state_data_std"]),dtype=torch.float32)
    ac=torch.as_tensor(raw[:,:,R.ACTION_COLS],dtype=torch.float32)
    pred,*_=ref.rollout(st.clone(),ac,START,action_offset=1)
    hold=st.clone(); hold[:,START:]=st[:,START-1:START].expand(-1,400-START,-1)
    a=((pred[:,START:]-st[:,START:])**2).numpy()
    b=((hold[:,START:]-st[:,START:])**2).numpy()
    return a,b,idx[:,0],ep[idx[:,0]]

print("="*94); print("TASK A / B -- GATING R-27"); print("="*94)
print(f"  {N_BIG} trajectories x {len(list(SEEDS))} eval seeds, released checkpoint, offset=1\n")
SQ_M, SQ_F, ROWS, EPS = [], [], [], []
for s in SEEDS:
    a,b,r,e = sq_err(s); SQ_M.append(a); SQ_F.append(b); ROWS.append(r); EPS.append(e)
    print(f"    seed {s} rolled out", flush=True)

# ---------------------------------------------------------------- A1
print("\n"+"="*94); print("A1 -- IS THE GRAVITY GROUP DRIVING IT?"); print("="*94)
print("  How the aggregate is computed. Our nrmse_per_step uses FORM 2:")
print("    form 1  RMSE pooled over all dims / mean(scale)  = sqrt(mean_d MSE_d) / mean_d(scale_d)")
print("    form 2  mean over dims of (RMSE_d / scale_d)     <- IMPLEMENTED, and used in R-27")
print("  They differ enormously when scales span 34x, so both are reported.\n")
mse_m = np.concatenate(SQ_M,0).mean(0)   # (T',45) pooled over all seeds+trajectories
mse_f = np.concatenate(SQ_F,0).mean(0)
rmse_m, rmse_f = np.sqrt(mse_m), np.sqrt(mse_f)          # (T',45)
pd_m = (rmse_m/scale).mean(0)                            # per-dim nRMSE, averaged over steps
pd_f = (rmse_f/scale).mean(0)
lose = pd_m > pd_f
print(f"  per-dimension nRMSE at h=368 (pooled over {len(SQ_M)*N_BIG} trajectories)")
print(f"    {'dim':<12s} {'scale':>8s} {'model':>9s} {'floor':>9s} {'ratio':>7s}  loses?")
for i in range(45):
    mark = "  LOSES" if lose[i] else ""
    if i<9 or lose[i] or i%12==0:
        print(f"    {NAMES[i]:<12s} {scale[i]:>8.4f} {pd_m[i]:>9.4f} {pd_f[i]:>9.4f} {pd_m[i]/pd_f[i]:>7.3f}{mark}")
print(f"\n  MODEL LOSES ON {int(lose.sum())} OF 45 DIMENSIONS: {[NAMES[i] for i in np.flatnonzero(lose)]}")

grav=[6,7,8]; keep=[i for i in range(45) if i not in grav]
f2_all, f2_ng = pd_m.mean(), pd_m[keep].mean()
f2_all_f, f2_ng_f = pd_f.mean(), pd_f[keep].mean()
f1_all = np.sqrt(mse_m.mean(1)).mean()/scale.mean()
f1_all_f = np.sqrt(mse_f.mean(1)).mean()/scale.mean()
f1_ng = np.sqrt(mse_m[:,keep].mean(1)).mean()/scale[keep].mean()
f1_ng_f = np.sqrt(mse_f[:,keep].mean(1)).mean()/scale[keep].mean()
print(f"\n  {'aggregation':<44s} {'model':>9s} {'floor':>9s} {'ratio':>7s}  verdict")
for lbl,m_,f_ in (("form 2, all 45 dims (as in R-27)",f2_all,f2_all_f),
                  ("form 2, 42 dims, gravity EXCLUDED",f2_ng,f2_ng_f),
                  ("form 1, all 45 dims",f1_all,f1_all_f),
                  ("form 1, 42 dims, gravity EXCLUDED",f1_ng,f1_ng_f)):
    print(f"  {lbl:<44s} {m_:>9.4f} {f_:>9.4f} {m_/f_:>7.3f}  {'model LOSES' if m_>f_ else 'model beats floor'}")

# ---------------------------------------------------------------- A2
print("\n"+"="*94); print("A2 -- IS THE HEAVY TAIL ONE REGION SAMPLED REPEATEDLY?"); print("="*94)
per_traj = np.concatenate([ (a/scale**2).sum((1,2)) for a in SQ_M ])   # scale-normalised total sq err
rows_all = np.concatenate(ROWS); eps_all = np.concatenate(EPS)
order = np.argsort(per_traj)[::-1]
tot = per_traj.sum(); k5 = max(1,int(0.05*len(per_traj)))
print(f"  {len(per_traj)} trajectories (with overlap), per-trajectory total normalised squared error")
print(f"    worst 5% ({k5} trajectories) carry {100*per_traj[order[:k5]].sum()/tot:.1f}% of the total")
print(f"    worst 1%  carry {100*per_traj[order[:max(1,len(per_traj)//100)]].sum()/tot:.1f}%")
print(f"    median {np.median(per_traj):.1f}   mean {per_traj.mean():.1f}   max {per_traj.max():.1f}"
      f"   max/median {per_traj.max()/np.median(per_traj):.0f}x")
tail_rows = rows_all[order[:k5]]; tail_eps = eps_all[order[:k5]]
print(f"\n  tail trajectories: episodes {sorted(set(tail_eps.tolist()))},"
      f" start rows {np.sort(tail_rows)[:12].tolist()}{' ...' if k5>12 else ''}")
srt=np.sort(tail_rows); clusters=[[srt[0]]]
for r_ in srt[1:]:
    if r_-clusters[-1][-1] < 400: clusters[-1].append(r_)
    else: clusters.append([r_])
print(f"  DISTINCT NON-OVERLAPPING TAIL REGIONS (gap >= 400 rows): {len(clusters)}")
for c in clusters:
    print(f"    rows {min(c)}-{max(c)}  (episode {ep[min(c)]}, {len(c)} tail trajectories)")

print("\n  restricted to strictly NON-OVERLAPPING trajectories:")
no_starts=[]
for e_ in split["holdout_episodes"]:
    idxs=np.flatnonzero(ep==e_); s0,s1=idxs[0],idxs[-1]
    c=s0
    while c+400-1<=s1: no_starts.append(c); c+=400
print(f"    {len(no_starts)} non-overlapping 400-step trajectories exist: {no_starts}")
idx_no=np.array(no_starts)[:,None]+np.arange(400)[None,:]
raw=data[idx_no]
st=torch.as_tensor(R.normalise_state(raw[:,:,R.STATE_COLS],cfg["state_data_mean"],cfg["state_data_std"]),dtype=torch.float32)
ac=torch.as_tensor(raw[:,:,R.ACTION_COLS],dtype=torch.float32)
pr,*_=ref.rollout(st.clone(),ac,START,action_offset=1)
hd=st.clone(); hd[:,START:]=st[:,START-1:START].expand(-1,400-START,-1)
sm=((pr[:,START:]-st[:,START:])**2).numpy(); sf=((hd[:,START:]-st[:,START:])**2).numpy()
pt=(sm/scale**2).sum((1,2))
print(f"    per-trajectory totals: {np.round(pt,1).tolist()}")
print(f"    max/median = {pt.max()/np.median(pt):.1f}x  -> "
      f"{'tail SURVIVES' if pt.max()/np.median(pt)>3 else 'no strong tail'}")
nm=(np.sqrt(sm.mean(0))/scale).mean(); nf=(np.sqrt(sf.mean(0))/scale).mean()
print(f"    nRMSE model {nm:.4f}  floor {nf:.4f}  -> "
      f"{'model LOSES' if nm>nf else 'model beats floor'} on non-overlapping trajectories only")

# ---------------------------------------------------------------- B
print("\n"+"="*94); print("TASK B -- IS THE BIAS JENSEN? AND THE POOLED ESTIMATOR"); print("="*94)
print("  Nested subsamples of each seed's 400 trajectories, so all n share one pool.\n")
print(f"  {'n':>5s} | {'mean_s MSE':>13s} | {'sqrt(mean_s MSE)':>17s} | {'mean_s sqrt(MSE)':>17s} | {'bias':>8s}")
print("  " + "-"*74)
rowsB={}
for n in (10,25,50,100,400):
    mses=[]; roots=[]
    for a in SQ_M:
        sub=a[:n]                                  # (n, T', 45)
        mse=sub.mean(0)                            # (T',45) unbiased
        mses.append(mse)
        roots.append((np.sqrt(mse)/scale).mean())   # per-seed nRMSE (the biased form)
    mse_bar=np.mean(mses,0)
    r1=float((mse_bar/scale**2).mean())            # mean over seeds of MSE (normalised)
    r2=float((np.sqrt(mse_bar)/scale).mean())      # sqrt AFTER averaging -> pooled estimator
    r3=float(np.mean(roots))                       # mean over seeds of sqrt -> per-seed averaged
    rowsB[n]={"mean_MSE":r1,"sqrt_of_mean_MSE":r2,"mean_of_sqrt_MSE":r3,"bias":r2-r3}
    print(f"  {n:>5d} | {r1:>13.5f} | {r2:>17.5f} | {r3:>17.5f} | {r2-r3:>8.5f}")
f=lambda k: np.array([rowsB[n][k] for n in (10,25,50,100,400)])
print(f"\n  variation across n (max/min):  mean_s MSE {f('mean_MSE').max()/f('mean_MSE').min():.3f}x"
      f"   sqrt(mean_s MSE) {f('sqrt_of_mean_MSE').max()/f('sqrt_of_mean_MSE').min():.3f}x"
      f"   mean_s sqrt(MSE) {f('mean_of_sqrt_MSE').max()/f('mean_of_sqrt_MSE').min():.3f}x")
jensen = (f('mean_MSE').max()/f('mean_MSE').min()<1.05 and
          f('sqrt_of_mean_MSE').max()/f('sqrt_of_mean_MSE').min()<1.05 and
          f('mean_of_sqrt_MSE')[-1]>f('mean_of_sqrt_MSE')[0]*1.2)
print(f"\n  M-17's mechanism is JENSEN'S INEQUALITY: {'PROVEN' if jensen else 'NOT established'}")
print(f"    E[sqrt(MSE_n)] < sqrt(E[MSE_n]); the gap grows with Var(MSE_n), which small n inflates.")
print(f"    pooled (unbiased) nRMSE = {rowsB[400]['sqrt_of_mean_MSE']:.4f}"
      f"   vs per-seed-averaged at n=10 = {rowsB[10]['mean_of_sqrt_MSE']:.4f}"
      f"  ({100*(1-rowsB[10]['mean_of_sqrt_MSE']/rowsB[400]['sqrt_of_mean_MSE']):.0f}% low)")
pooled_floor=float((np.sqrt(np.mean([b.mean(0) for b in SQ_F],0))/scale).mean())
print(f"\n  POOLED estimator, released checkpoint vs floor at h=368:")
print(f"    model {rowsB[400]['sqrt_of_mean_MSE']:.4f}   floor {pooled_floor:.4f}"
      f"   -> {'model LOSES' if rowsB[400]['sqrt_of_mean_MSE']>pooled_floor else 'model beats floor'}")

json.dump({"per_dim_model":pd_m.tolist(),"per_dim_floor":pd_f.tolist(),"dim_names":NAMES,
           "n_dims_lost":int(lose.sum()),"dims_lost":[NAMES[i] for i in np.flatnonzero(lose)],
           "aggregations":{"form2_all":float(f2_all),"form2_all_floor":float(f2_all_f),
                           "form2_nogravity":float(f2_ng),"form2_nogravity_floor":float(f2_ng_f),
                           "form1_all":float(f1_all),"form1_all_floor":float(f1_all_f),
                           "form1_nogravity":float(f1_ng),"form1_nogravity_floor":float(f1_ng_f)},
           "tail":{"worst5pct_share":float(per_traj[order[:k5]].sum()/tot),
                   "n_distinct_regions":len(clusters),
                   "regions":[[int(min(c)),int(max(c)),int(ep[min(c)])] for c in clusters],
                   "nonoverlap_starts":[int(x) for x in no_starts],
                   "nonoverlap_per_traj":pt.tolist(),
                   "nonoverlap_nrmse_model":float(nm),"nonoverlap_nrmse_floor":float(nf)},
           "jensen":{str(k):v for k,v in rowsB.items()},"jensen_proven":bool(jensen),
           "pooled_model":rowsB[400]["sqrt_of_mean_MSE"],"pooled_floor":pooled_floor},
          open(os.path.join(R.RESULTS,"taskAB_gate_r27.json"),"w"),indent=2)
print(f"\n  wrote {R.rel(os.path.join(R.RESULTS,'taskAB_gate_r27.json'))}")
