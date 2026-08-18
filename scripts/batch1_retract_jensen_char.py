"""
Task 1 (verification of the retraction's specific numbers), Task 2 (Jensen at 40 seeds),
Task 3b (characterise the released checkpoint on all ten episodes, independent trajectories).

The whole pool of 1,202 valid held-out start points is rolled out ONCE and stored, so the
40-seed resampling in Task 2 is exact and costs no extra rollouts.
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np, torch
import rwm_data as R, rollout_eval as E, rwm_metrics as MET, score_reference as S

START, LEN = E.START_STEP, 400
GRAV = [6, 7, 8]; KEEP = [i for i in range(45) if i not in GRAV]
NAMES = (["v_x","v_y","v_z","w_x","w_y","w_z","g_x","g_y","g_z"]
         + [f"q_{l}_{a}" for a in ("HAA","HFE","KFE") for l in ("LF","LH","RF","RH")]
         + [f"qd_{l}_{a}" for a in ("HAA","HFE","KFE") for l in ("LF","LH","RF","RH")]
         + [f"tau_{l}_{a}" for a in ("HAA","HFE","KFE") for l in ("LF","LH","RF","RH")])
GROUPS = [("base lin vel", R.LIN_VEL), ("base ang vel", R.ANG_VEL), ("proj gravity", R.GRAVITY),
          ("joint pos", R.JOINT_POS), ("joint vel", R.JOINT_VEL), ("joint torque", R.JOINT_TAU)]

paths=R.repo_paths(); cfg=R.load_reference_config(paths["lite"])
data,ep=R.load_data(paths["csv"],verbose=False)
split=E.make_split(seed=0,strat_path=os.path.join(R.RESULTS,"step0_strat.json"),verbose=False)
scale=MET.training_scale(data,ep,split["train_episodes"],cfg["state_data_mean"],cfg["state_data_std"])
ref=S.ReferenceRWM(torch.load(paths["ckpt"],map_location="cpu")["system_dynamics_state_dict"])
out={}

def roll(starts, chunk=200):
    """Squared error for model and floor over the given starts."""
    A,B=[],[]
    for i in range(0,len(starts),chunk):
        idx=np.asarray(starts[i:i+chunk])[:,None]+np.arange(LEN)[None,:]
        raw=data[idx]
        st=torch.as_tensor(R.normalise_state(raw[:,:,R.STATE_COLS],cfg["state_data_mean"],
                                             cfg["state_data_std"]),dtype=torch.float32)
        ac=torch.as_tensor(raw[:,:,R.ACTION_COLS],dtype=torch.float32)
        pr,*_=ref.rollout(st.clone(),ac,START,action_offset=1)
        hd=st.clone(); hd[:,START:]=st[:,START-1:START].expand(-1,LEN-START,-1)
        A.append(((pr[:,START:]-st[:,START:])**2).numpy().astype(np.float32))
        B.append(((hd[:,START:]-st[:,START:])**2).numpy().astype(np.float32))
    return np.concatenate(A,0), np.concatenate(B,0)

# ================================================================= TASK 1
print("="*94); print("TASK 1 -- VERIFYING THE RETRACTION'S SPECIFIC NUMBERS"); print("="*94)
pool=[s for s in R.valid_window_starts(ep,LEN) if ep[s] in split["holdout_episodes"]]
print(f"  rolling out the entire held-out pool: {len(pool)} start points (one pass)...", flush=True)
SQM,SQF=roll(pool)
print(f"  done, stored {SQM.nbytes/1e6:.0f} MB\n")
mse_m,mse_f=SQM.mean(0),SQF.mean(0)
pd_m=(np.sqrt(mse_m)/scale).mean(0); pd_f=(np.sqrt(mse_f)/scale).mean(0)
tot=pd_m.sum()
print(f"  form-2 sum over 45 dims = {tot:.2f}")
print(f"    g_z alone            = {pd_m[8]:.2f}  ({100*pd_m[8]/tot:.0f}% of the sum)")
print(f"    all three gravity    = {pd_m[GRAV].sum():.2f}  ({100*pd_m[GRAV].sum()/tot:.0f}%)")
lose=pd_m>pd_f
print(f"    model loses on {int(lose.sum())} of 45 dims: {[NAMES[i] for i in np.flatnonzero(lose)]}")
print(f"\n  the g_z defect (the narrow claim that survives):")
print(f"    model {pd_m[8]:.4f}   floor {pd_f[8]:.4f}   ratio {pd_m[8]/pd_f[8]:.1f}x")
cfg_std=cfg["state_data_std"][8]; true_raw=cfg_std*scale[8]
print(f"\n  why this dimension is strange:")
print(f"    config state_data_std[g_z]      = {cfg_std}")
print(f"    measured normalised spread      = {scale[8]:.4f}")
print(f"    implied TRUE raw spread         = {cfg_std}*{scale[8]:.4f} = {true_raw:.6f}")
print(f"    config overestimates it by        {cfg_std/true_raw:.1f}x")
print(f"    squared-error weight in the loss vs a correctly scaled dim: "
      f"1/{(cfg_std/true_raw)**2:.0f}x  ({np.log10((cfg_std/true_raw)**2):.1f} orders of magnitude)")
out["task1"]={"form2_sum":float(tot),"gz_share":float(pd_m[8]/tot),
              "gravity_share":float(pd_m[GRAV].sum()/tot),"n_dims_lost":int(lose.sum()),
              "dims_lost":[NAMES[i] for i in np.flatnonzero(lose)],
              "gz_model":float(pd_m[8]),"gz_floor":float(pd_f[8]),
              "gz_ratio":float(pd_m[8]/pd_f[8]),"config_std_gz":float(cfg_std),
              "measured_norm_spread":float(scale[8]),"true_raw_spread":float(true_raw),
              "overestimate_factor":float(cfg_std/true_raw),
              "loss_weight_factor":float((cfg_std/true_raw)**2)}

# ================================================================= TASK 2
print("\n"+"="*94); print("TASK 2 -- JENSEN AT 40 SEEDS (resampled from the stored pool)"); print("="*94)
NS=(10,25,50,100,400); SEEDS=40
print(f"  {'n':>5s} | {'mean_s MSE':>13s} | {'sqrt(mean_s MSE)':>17s} | {'mean_s sqrt(MSE)':>17s} | {'bias':>8s} | {'n_ind':>6s}")
print("  "+"-"*88)
rows={}
for n in NS:
    mses=[];roots=[];ninds=[]
    for s in range(SEEDS):
        rs=np.random.default_rng(1000+s)
        sel=rs.choice(len(pool),size=n,replace=False)
        mse=SQM[sel].mean(0); mses.append(mse)
        roots.append(float((np.sqrt(mse)/scale).mean()))
        ninds.append(MET.n_independent([pool[i] for i in sel],LEN))
    mb=np.mean(mses,0)
    r1=float((mb/scale**2).mean()); r2=float((np.sqrt(mb)/scale).mean()); r3=float(np.mean(roots))
    rows[n]={"mean_MSE":r1,"sqrt_of_mean_MSE":r2,"mean_of_sqrt_MSE":r3,"bias":r2-r3,
             "n_independent_mean":float(np.mean(ninds))}
    print(f"  {n:>5d} | {r1:>13.5f} | {r2:>17.5f} | {r3:>17.5f} | {r2-r3:>8.5f} | {np.mean(ninds):>6.1f}")
f=lambda k: np.array([rows[n][k] for n in NS])
v1=f('mean_MSE').max()/f('mean_MSE').min(); v2=f('sqrt_of_mean_MSE').max()/f('sqrt_of_mean_MSE').min()
v3=f('mean_of_sqrt_MSE')[-1]/f('mean_of_sqrt_MSE')[0]
print(f"\n  variation across n:  mean_s MSE {v1:.3f}x   sqrt(mean_s MSE) {v2:.3f}x   mean_s sqrt(MSE) {v3:.3f}x")
flat=v1<1.05
print(f"  mean_s MSE flat to within 5%? {flat}")
supported = v2<1.10 and f('mean_of_sqrt_MSE')[-1]>f('mean_of_sqrt_MSE')[0]*1.15
print(f"  VERDICT on the Jensen mechanism: {'SUPPORTED' if supported else 'not supported'}")
print(f"    criterion: sqrt(mean_s MSE) flat AND mean_s sqrt(MSE) rising toward it.")
if not flat:
    print(f"    NOTE: mean_s MSE still varies {v1:.2f}x at 40 seeds. It is the mean of a")
    print(f"    quantity with per-trajectory max/median ~2900x, so its own standard error is")
    print(f"    large at any feasible seed count; it is not diagnostic of the mechanism.")
print(f"  estimator conclusion (independent of the mechanism): per-seed-averaged nRMSE at n=10")
print(f"    is {100*(1-rows[10]['mean_of_sqrt_MSE']/rows[400]['sqrt_of_mean_MSE']):.0f}% below the pooled form.")
out["task2"]={"seeds":SEEDS,"rows":{str(k):v for k,v in rows.items()},
              "mean_MSE_variation":float(v1),"sqrt_mean_variation":float(v2),
              "supported":bool(supported),"mean_MSE_flat":bool(flat)}

# ================================================================= TASK 3b
print("\n"+"="*94); print("TASK 3b -- RELEASED CHECKPOINT ON ALL TEN EPISODES, INDEPENDENT TRAJECTORIES"); print("="*94)
allst=MET.non_overlapping_starts(ep,range(R.N_EPISODES),LEN)
print(f"  {len(allst)} non-overlapping {LEN}-step trajectories across all 10 episodes")
print(f"    starts {allst}")
print(f"    n_independent = {MET.n_independent(allst,LEN)} (by construction)")
print(f"  Justification: the released checkpoint was trained on the entire CSV, so restricting")
print(f"  it to the two held-out episodes buys nothing -- the leakage is already total.\n")
AM,AF=roll(allst)
print(f"  {'h':>4s} | {'relL1 mdl':>10s} {'relL1 flr':>10s} | {'form1 mdl':>10s} {'form1 flr':>10s}"
      f" | {'form2 mdl':>10s} {'form2 flr':>10s} | {'f1 no-g':>9s}")
hz={}
for h in (1,4,8,16,32,64,128,256,368):
    sm,sf=AM[:,:h],AF[:,:h]
    st_=None
    e_m=float(np.mean([ (np.sqrt(sm)[:, :, :]).sum() ]))  # placeholder removed below
    hz[h]={"form1":MET.nrmse_pooled(sm,scale),"form1_floor":MET.nrmse_pooled(sf,scale),
           "form2":MET.nrmse_form2(sm,scale),"form2_floor":MET.nrmse_form2(sf,scale),
           "form1_nog":MET.nrmse_pooled(sm,scale,KEEP),"form1_nog_floor":MET.nrmse_pooled(sf,scale,KEEP)}
# relative-L1 needs the signed error, recompute from the true states
def rel_l1(starts,h):
    idx=np.asarray(starts)[:,None]+np.arange(LEN)[None,:]
    raw=data[idx]
    st=torch.as_tensor(R.normalise_state(raw[:,:,R.STATE_COLS],cfg["state_data_mean"],cfg["state_data_std"]),dtype=torch.float32)
    ac=torch.as_tensor(raw[:,:,R.ACTION_COLS],dtype=torch.float32)
    pr,*_=ref.rollout(st.clone(),ac,START,action_offset=1)
    hd=st.clone(); hd[:,START:]=st[:,START-1:START].expand(-1,LEN-START,-1)
    def g(p):
        nu=(p[:,START:START+h]-st[:,START:START+h]).abs().sum(-1); de=st[:,START:START+h].abs().sum(-1)
        return float((nu/de).mean())
    return g(pr),g(hd)
for h in hz:
    a,b=rel_l1(allst,h); hz[h]["relL1"]=a; hz[h]["relL1_floor"]=b
    r=hz[h]
    print(f"  {h:>4d} | {r['relL1']:>10.4f} {r['relL1_floor']:>10.4f} | {r['form1']:>10.4f} {r['form1_floor']:>10.4f}"
          f" | {r['form2']:>10.4f} {r['form2_floor']:>10.4f} | {r['form1_nog']:>9.4f}")
r=hz[368]
print(f"\n  AT h=368, n_independent=20, the released checkpoint:")
for lbl,m_,f_ in (("relative-L1",r['relL1'],r['relL1_floor']),
                  ("nRMSE form 1 (primary)",r['form1'],r['form1_floor']),
                  ("nRMSE form 1, no gravity",r['form1_nog'],r['form1_nog_floor']),
                  ("nRMSE form 2 (legacy)",r['form2'],r['form2_floor'])):
    print(f"    {lbl:<28s} {m_:>8.4f} vs floor {f_:>8.4f}  -> "
          f"{'BEATS' if m_<f_ else 'LOSES'} by {abs(1-m_/f_)*100:.0f}%")
mse_a,mse_b=AM.mean(0),AF.mean(0)
pdm=(np.sqrt(mse_a)/scale).mean(0); pdf=(np.sqrt(mse_b)/scale).mean(0); ls=pdm>pdf
print(f"\n  per-dimension: model loses on {int(ls.sum())} of 45 -> {[NAMES[i] for i in np.flatnonzero(ls)]}")
print(f"  per-group (form 1 pooled within group):")
for nm,cols in GROUPS:
    c=list(cols)
    print(f"    {nm:<14s} model {MET.nrmse_pooled(AM,scale,c):>8.4f}  floor {MET.nrmse_pooled(AF,scale,c):>8.4f}")
out["task3b"]={"starts":allst,"n_independent":MET.n_independent(allst,LEN),
               "horizons":{str(k):v for k,v in hz.items()},
               "n_dims_lost":int(ls.sum()),"dims_lost":[NAMES[i] for i in np.flatnonzero(ls)],
               "per_dim_model":pdm.tolist(),"per_dim_floor":pdf.tolist(),
               "groups":{nm:{"model":MET.nrmse_pooled(AM,scale,list(c)),
                             "floor":MET.nrmse_pooled(AF,scale,list(c))} for nm,c in GROUPS}}
json.dump(out,open(os.path.join(R.RESULTS,"batch1_post_retraction.json"),"w"),indent=2)
print(f"\n  wrote {R.rel(os.path.join(R.RESULTS,'batch1_post_retraction.json'))}")
