"""
Task 2 -- sigma per forecast step WITHIN the trained horizon (steps 1-8), all models.

Two readings, stated before the numbers:
  sigma GROWS across 1-8 then flattens -> the model learned horizon-dependent uncertainty
    where the loss asked for it and cannot extrapolate beyond. Structural limitation of the
    8-step forecast objective, and constructive: a longer horizon might fix it.
  sigma FLAT across 1-8 too -> it fails to learn horizon-dependence even where the loss
    demanded it. Stronger negative result; removes the structural excuse.

Arm B is included because Task 6's per-checkpoint limitations table needs it.
"""
import json, os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "src"))
import numpy as np, torch
import rwm_data as R, rollout_eval as E, rwm_metrics as MET, rwm_model as M, score_reference as S
START=E.START_STEP; SEEDS=(0,1,2)
paths=R.repo_paths(); cfg=R.load_reference_config(paths["lite"])
data,ep=R.load_data(paths["csv"],verbose=False)
split=E.make_split(seed=0,strat_path=os.path.join(R.RESULTS,"step0_strat.json"),verbose=False)
starts=MET.non_overlapping_starts(ep,list(split["holdout_episodes"]),400)
idx=np.asarray(starts)[:,None]+np.arange(400)[None,:]
raw=data[idx]
ST=torch.as_tensor(R.normalise_state(raw[:,:,R.STATE_COLS],cfg["state_data_mean"],cfg["state_data_std"]),dtype=torch.float32)
AC=torch.as_tensor(raw[:,:,R.ACTION_COLS],dtype=torch.float32)
def get(run,ck=2500):
    m=M.build_from_config(cfg,ensemble_size=1)
    m.load_state_dict(torch.load(f"runs/{run}/weights_{ck}.pt",map_location="cpu")["model_state_dict"],strict=True)
    m.eval(); return m
MODELS={
 "faithful armA (mse)":[get(f"armA_seed{s}") for s in SEEDS],
 "corrected armA (nll)":[get(f"armA_seed{s}_nll") for s in SEEDS],
 "teacher-forced armB":[get(f"armB_seed{s}") for s in SEEDS],
 "released checkpoint":[S.ReferenceRWM(torch.load(paths["ckpt"],map_location="cpu")["system_dynamics_state_dict"])],
}
print("="*100); print("TASK 2 -- SIGMA PROFILE WITHIN THE TRAINED HORIZON (forecast steps 1-8)"); print("="*100)
print(f"  held-out episodes {split['holdout_episodes']}, {len(starts)} independent trajectories")
print("  the loss trains on exactly these 8 forecast steps (forecast_horizon = 8)\n")
out={}
for name,ms in MODELS.items():
    Es,Ss=[],[]
    for m in ms:
        pr,sg=m.rollout_full(ST.clone(),AC,START,action_offset=1)
        Es.append((pr[:,START:]-ST[:,START:]).abs().numpy()); Ss.append(sg[:,START:].numpy())
    err=np.concatenate(Es,0); sig=np.concatenate(Ss,0)
    z=err/np.maximum(sig,1e-30)
    sp=[float(sig[:,i].mean()) for i in range(8)]
    ep_=[float(err[:,i].mean()) for i in range(8)]
    c1=[float((z[:,i]<=1).mean()) for i in range(8)]
    c2=[float((z[:,i]<=2).mean()) for i in range(8)]
    growth=sp[7]/sp[0]
    late=float(sig[:,300:].mean())/sp[0]
    out[name]={"sigma_by_step":sp,"err_by_step":ep_,"cov1_by_step":c1,"cov2_by_step":c2,
               "sigma_growth_1_to_8":growth,"sigma_growth_1_to_late":late,
               "err_growth_1_to_8":ep_[7]/ep_[0]}
    print(f"  {name.upper()}")
    print(f"    {'step':>5s} {'sigma':>12s} {'sigma/s1':>9s} {'mean|err|':>11s} {'err/s1':>8s} {'cov+-1s':>9s} {'cov+-2s':>9s}")
    for i in range(8):
        print(f"    {i+1:>5d} {sp[i]:>12.6e} {sp[i]/sp[0]:>9.4f} {ep_[i]:>11.4e}"
              f" {ep_[i]/ep_[0]:>8.2f} {100*c1[i]:>8.2f}% {100*c2[i]:>8.2f}%")
    print(f"    sigma grows {growth:.4f}x from step 1 to 8, while |error| grows {ep_[7]/ep_[0]:.2f}x")
    print(f"    sigma at steps 300+ vs step 1: {late:.4f}x\n")
print("="*100); print("  WHICH READING DOES THE DATA SUPPORT?"); print("="*100)
FLAT=1.05
for name,v in out.items():
    g=v["sigma_growth_1_to_8"]; e=v["err_growth_1_to_8"]
    verdict = "FLAT -- fails to learn horizon-dependence where the loss demanded it" if g<FLAT \
              else f"GROWS {g:.2f}x -- learned some horizon-dependence"
    print(f"  {name:<24s} sigma x{g:.4f} vs error x{e:.2f}  ->  {verdict}")
allflat=all(v["sigma_growth_1_to_8"]<FLAT for v in out.values())
print()
if allflat:
    print("  READING 2 -- THE STRONGER NEGATIVE RESULT.")
    print("  sigma is flat across steps 1-8 in every model, INCLUDING the corrected arm and")
    print("  INCLUDING the released checkpoint, while the realised error grows several-fold")
    print("  over the same range. The models fail to learn horizon-dependence even inside the")
    print("  window the loss actually optimises. The structural excuse -- that the 8-step")
    print("  objective cannot teach uncertainty beyond 8 steps -- does not apply, because")
    print("  they do not learn it within 8 steps either.")
    print("  The coverage decline from step 1 to 8 is therefore driven ENTIRELY by growing")
    print("  error against a fixed sigma, not by sigma failing to keep up.")
else:
    print("  READING 1 -- at least one model learned horizon-dependence within the trained range.")
json.dump(out,open(os.path.join(R.RESULTS,"task2_sigma_profile.json"),"w"),indent=2)
print(f"\n  wrote {R.rel(os.path.join(R.RESULTS,'task2_sigma_profile.json'))}")
