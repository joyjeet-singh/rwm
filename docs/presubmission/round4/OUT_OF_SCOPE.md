# Round-4 out of scope

One line per item, with file:line. Logged, not fixed (PLAN.md §1.1).
- F0 (PF4): `lite/scripts/envs/anymal_d_flat.py:105` computes `joint_acc = (joint_vel - self.last_obs["policy"][:, 12:24]) / self._step_dt`, and columns 12:24 of the policy observation built at `:53` are the joint positions (the command sits at 9:12), not the velocities. So the released imagination reward's `dof_acc_l2` term (`:117`, weight -2.5e-7 at `lite/scripts/configs/anymal_d_flat_cfg.py:22`) penalises velocity minus position. Neither the paper (§7 lists the released pipeline's defects) nor the ledger mentions it (grep `dof_acc|joint_acc`). Whether it matters to X5, and whether §7 should report it, is not F0's call.
