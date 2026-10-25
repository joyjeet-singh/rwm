"""Locate and characterise every large adjacent-row discontinuity."""
import os
import numpy as np
import pandas as pd

CSV = os.path.expanduser("~/Downloads/PDM/robotic_world_model_lite/assets/data/state_action_data_0.csv")
JOINT_POS = list(range(9, 21))
JOINT_VEL = list(range(21, 33))
JOINT_TAU = list(range(33, 45))
LIN_VEL = list(range(0, 3))
ANG_VEL = list(range(3, 6))
GRAV = list(range(6, 9))
ACT = list(range(45, 57))
CONTACT = list(range(57, 65))
DT = 0.02

d = pd.read_csv(CSV, header=None).to_numpy(np.float64)
dq = np.abs(np.diff(d[:, JOINT_POS], axis=0)).max(axis=1)

print("=== top 25 adjacent-row joint-position jumps ===")
order = np.argsort(dq)[::-1][:25]
for i in order:
    print(f"  row {i:5d}->{i+1:5d}   max|dq| {dq[i]:.5f} rad")

print("\n=== jumps above 0.30 rad ===")
big = np.flatnonzero(dq > 0.30)
print(f"  {len(big)} of {len(dq)} pairs: {big.tolist()}")

print("\n=== jumps at every multiple of 1000 (row k-1 -> k) ===")
for k in range(1000, 10000, 1000):
    print(f"  row {k-1:5d}->{k:5d}   max|dq| {dq[k-1]:.5f} rad")

print("\n=== distribution of max|dq| ===")
for p in (50, 90, 99, 99.9, 99.99, 100):
    print(f"  p{p:<6} {np.percentile(dq, p):.5f} rad")
print(f"  pairs > 0.5: {int((dq > 0.5).sum())}   > 0.4: {int((dq > 0.4).sum())}"
      f"   > 0.3: {int((dq > 0.3).sum())}   > 0.25: {int((dq > 0.25).sum())}")

print("\n=== which joint jumps at 998->999 ===")
delta = d[999, JOINT_POS] - d[998, JOINT_POS]
LEGS = ["LF", "LH", "RF", "RH"]
NAMES = [f"{l}_{j}" for j in ("HAA", "HFE", "KFE") for l in LEGS]
for j in range(12):
    print(f"  {NAMES[j]:8s} q {d[998, JOINT_POS[j]]:+8.4f} -> {d[999, JOINT_POS[j]]:+8.4f}"
          f"   d {delta[j]:+8.4f} rad   ({delta[j]/DT:+8.2f} rad/s implied)")

print("\n=== joint velocity consistency across 998->999 ===")
print("  implied dq/dt vs recorded qdot at row 998 and 999")
for j in range(12):
    print(f"  {NAMES[j]:8s} implied {delta[j]/DT:+8.2f}   qdot[998] {d[998, JOINT_VEL[j]]:+8.2f}"
          f"   qdot[999] {d[999, JOINT_VEL[j]]:+8.2f}")

print("\n=== other channels across 995..1002 ===")
for r in range(995, 1003):
    print(f"  row {r}:  v {d[r, LIN_VEL].round(3)}  w {d[r, ANG_VEL].round(3)}"
          f"  g {d[r, GRAV].round(4)}  contacts {d[r, CONTACT].astype(int)}"
          f"  term {int(d[r, 65])}")

print("\n=== per-group max jump at 998->999 vs global p99 ===")
for name, cols in (("lin vel", LIN_VEL), ("ang vel", ANG_VEL), ("gravity", GRAV),
                   ("q", JOINT_POS), ("qdot", JOINT_VEL), ("tau", JOINT_TAU),
                   ("action", ACT)):
    dd = np.abs(np.diff(d[:, cols], axis=0)).max(axis=1)
    print(f"  {name:8s} at 998->999 {dd[998]:9.4f}   p99 {np.percentile(dd, 99):9.4f}"
          f"   max {dd.max():9.4f} at row {int(np.argmax(dd))}   ratio {dd[998]/np.percentile(dd,99):6.2f}x")

print("\n=== gravity-vector angular step (deg) around the jump ===")
g = d[:, GRAV] / np.linalg.norm(d[:, GRAV], axis=1, keepdims=True)
cosang = np.clip((g[:-1] * g[1:]).sum(axis=1), -1, 1)
ang = np.degrees(np.arccos(cosang))
print(f"  at 998->999 {ang[998]:.4f} deg   p99 {np.percentile(ang, 99):.4f}   max {ang.max():.4f}"
      f" at row {int(np.argmax(ang))}")

print("\n=== is row 999 a jump, or is row 998 an outlier? ===")
print("  max|dq| for 996->997, 997->998, 998->999, 999->1000, 1000->1001")
for i in range(996, 1001):
    print(f"    {i}->{i+1}: {dq[i]:.5f}")
