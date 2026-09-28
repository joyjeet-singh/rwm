"""
What the three architecture baselines of rules M-75 and M-76 share with RWM, and with
each other. docs/presubmission/BASELINE_SPECS.md records every choice with its citation.

SHARED WITH RWM'S STATE PATHWAY, by reuse and not by copy:
  * the state head is rwm_model.MLPStateHead itself: the residual connection on the last
    input state (mlp.py:88) and the bounded, double-softplus log-sigma (mlp.py:91-93);
  * the regression loss is RWMEnsemble.compute_regression_loss with loss_type "mse", the
    faithful objective: squared error of a reparameterised SAMPLE, summed over the 45
    state dimensions, meaned over the batch (system_dynamics.py:270-289);
  * the bound loss is RWMEnsemble.compute_bound_loss (system_dynamics.py:301-302);
  * no auxiliary (contact, termination) heads: the comparison is state-only, and RWM's
    state prediction does not read its auxiliary branch (BASELINE_SPECS.md §1).

THE CAUSAL ACTION ALIGNMENT (D-13, X-05), identical to RWM's training slicing
(system_dynamics.py:196-200 in the lite release): the state in row t is paired with the
action in row t + 1, the action that produces state t + 1. So a model predicting state row
r always sees action row r as its newest action. action_rows_for() is the one place that
arithmetic lives, and the verification ladder asserts it (scripts/baseline_verification.py).

THE TWO REGIMES, over a training window of H history rows and F = window - H targets:
  ar  autoregressive, as Arm A: after each target the model's own reparameterised sample
      enters the history in place of the truth (the upstream MLP path slides its window,
      system_dynamics.py:216-224);
  tf  teacher-forced, as Arm B: every target is predicted from true inputs only.
"""
import torch
import torch.nn as nn

import rwm_model as M

STATE_DIM, ACTION_DIM = 45, 12


def action_rows_for(target_row, history):
    """Rows of the action window paired with a state window ending at target_row - 1.

    The state window is rows target_row - history ... target_row - 1; the action window is
    shifted one row later, target_row - history + 1 ... target_row, so its newest action is
    the one that produces the target state.
    """
    return target_row - history + 1, target_row + 1


def regression_loss(mean, std, target):
    """RWM's faithful objective, reused: sampled squared error, sum over dims, mean over batch."""
    return M.RWMEnsemble.compute_regression_loss(None, mean, std, target, "mse")[0]


def bound_loss(head):
    return M.RWMEnsemble.compute_bound_loss(head)


def state_head(input_dim, cfg):
    arch = cfg["architecture_config"]
    return M.MLPStateHead(input_dim, STATE_DIM, arch["state_mean_shape"],
                          arch["state_logstd_shape"])


def n_params(module):
    return sum(p.numel() for p in module.parameters())


class WindowModel(nn.Module):
    """A baseline that reads a fixed window of the last H (state, action) rows: MLP and
    transformer. Subclasses provide encode(x_state, x_action) -> (batch, features)."""

    def __init__(self, history, cfg, base_out):
        super().__init__()
        self.history = history
        self.head = state_head(base_out, cfg)

    def encode(self, x_state, x_action):
        raise NotImplementedError

    def predict(self, x_state, x_action):
        return self.head(self.encode(x_state, x_action), x_state)

    def reset(self):
        pass

    def compute_state_loss(self, state_batch, action_batch, regime):
        """(state, bound, kl) losses over the window's forecast targets, meaned over them."""
        H = self.history
        F = state_batch.shape[1] - H
        x_state = state_batch[:, :H]
        s_l, b_l = [], []
        for i in range(F):
            lo, hi = action_rows_for(H + i, H)
            x_action = action_batch[:, lo:hi]
            mean, std = self.predict(x_state, x_action)
            s_l.append(regression_loss(mean, std, state_batch[:, H + i]).unsqueeze(0))
            b_l.append(bound_loss(self.head).unsqueeze(0))
            if regime == "tf":
                x_state = state_batch[:, i + 1:H + i + 1]
            elif regime == "ar":
                sample = torch.randn_like(mean) * std + mean
                x_state = torch.cat([x_state[:, 1:], sample.unsqueeze(1)], dim=1)
            else:
                raise ValueError(regime)
        m = lambda L: torch.cat(L).mean()
        return m(s_l), m(b_l), torch.zeros((), device=state_batch.device)

    @torch.no_grad()
    def rollout(self, state, action, start_step, action_offset=1):
        """Autoregressive rollout from start_step history rows, feeding back the mean, as
        RWMEnsemble.rollout does. action_offset=1 is the causal alignment."""
        assert action_offset == 1, "the baselines are evaluated with the causal alignment only"
        assert start_step >= self.history, "the history must fill the window"
        pred = state.clone()
        for i in range(start_step, state.shape[1]):
            lo, hi = action_rows_for(i, self.history)
            mean, _ = self.predict(pred[:, i - self.history:i], action[:, lo:hi])
            pred[:, i] = mean
        return pred
