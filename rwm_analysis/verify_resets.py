"""Test the hypothesis: rows 999, 1999, ... 9999 are post-reset initial states
that the termination column never marks."""
import os
import numpy as np
import pandas as pd

CSV = os.path.expanduser("~/Downloads/PDM/robotic_world_model_lite/assets/data/state_action_data_0.csv")
JP, JV, JT = list(range(9, 21)), list(range(21, 33)), list(range(33, 45))
GRAV, LV, AV = list(range(6, 9)), list(range(0, 3)), list(range(3, 6))
ACT, CON, TERM = list(range(45, 57)), list(range(57, 65)), 65
HAA = JP[0:4]

d = pd.read_csv(CSV, header=None).to_numpy(np.float64)
N = len(d)
cand = np.arange(999, N, 1000)

print("=== reset signature test on candidate rows 999,1999,...,9999 ===")
print("row     qdot all==0   g==(0,0,-1)   HAA all==0    tau all==0   action all==0   term")
for r in cand:
    print(f"{r:5d}   {str(np.all(d[r, JV] == 0.0)):>10}  "
          f"{str(np.array_equal(d[r, GRAV], [0.0, 0.0, -1.0])):>12}  "
          f"{str(np.all(d[r, HAA] == 0.0)):>11}  "
          f"{str(np.all(d[r, JT] == 0.0)):>11}  "
          f"{str(np.all(d[r, ACT] == 0.0)):>13}   {int(d[r, TERM])}")

print("\n=== do these signatures occur ANYWHERE else in the file? ===")
qdot_zero = np.flatnonzero(np.all(d[:, JV] == 0.0, axis=1))
g_exact = np.flatnonzero(np.all(d[:, GRAV] == np.array([0.0, 0.0, -1.0]), axis=1))
haa_zero = np.flatnonzero(np.all(d[:, HAA] == 0.0, axis=1))
tau_zero = np.flatnonzero(np.all(d[:, JT] == 0.0, axis=1))
print(f"  rows with all 12 qdot exactly 0 : {qdot_zero.tolist()}")
print(f"  rows with g exactly (0,0,-1)    : {g_exact.tolist()}")
print(f"  rows with all 4 HAA exactly 0   : {haa_zero.tolist()}")
print(f"  rows with all 12 tau exactly 0  : {tau_zero.tolist()}")

print("\n=== continuity ACROSS the candidate row (is it the new episode's first row?) ===")
print("  if row r starts a new episode, r->r+1 should be smooth and r-1->r should not")
dq = np.abs(np.diff(d[:, JP], axis=0)).max(axis=1)
dv = np.abs(np.diff(d[:, LV], axis=0)).max(axis=1)
for r in cand[:-1]:
    print(f"  r={r:5d}   dq[{r-1}->{r}] {dq[r-1]:.4f}  dq[{r}->{r+1}] {dq[r]:.4f}   |"
          f"  dv[{r-1}->{r}] {dv[r-1]:.4f}  dv[{r}->{r+1}] {dv[r]:.4f}")

print("\n=== segment structure implied ===")
starts = np.concatenate(([0], cand))
ends = np.concatenate((cand - 1, [N - 1]))
tot = 0
W = 40
for s, e in zip(starts, ends):
    L = e - s + 1
    w = max(0, L - W + 1)
    tot += w
    print(f"  rows {s:5d}..{e:5d}   length {L:5d}   valid {W}-windows {w:5d}")
print(f"  TOTAL valid {W}-step windows honouring resets: {tot}")
print(f"  vs termination-column-only count:              {N - W + 1}")
print(f"  overcount if you trust column 65:              {(N - W + 1) - tot}")

print("\n=== assertion 3 with reset rows excluded ===")
mask = np.ones(N - 1, dtype=bool)
mask[cand[cand < N - 1] - 1] = False          # pair (r-1 -> r) crossing into a reset
print(f"  max |dq| over all {N-1} pairs                  : {dq.max():.5f} rad")
print(f"  max |dq| over {int(mask.sum())} within-episode pairs      : {dq[mask].max():.5f} rad"
      f"  at row {int(np.argmax(np.where(mask, dq, -1)))}")
print(f"  p99 within-episode                            : {np.percentile(dq[mask], 99):.5f} rad")

print("\n=== contact flags at reset rows (are they stale?) ===")
for r in cand:
    prev = d[r - 1, CON].astype(int) if r > 0 else None
    print(f"  row {r:5d}  contacts {d[r, CON].astype(int)}   prev row {prev}"
          f"   identical={np.array_equal(d[r, CON], d[r-1, CON])}")
