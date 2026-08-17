"""
Step 4 / 1 -- the model, from scratch, with both the inference and training paths.

Module and parameter names mirror the reference exactly
(`state_base.memory.rnn.weight_ih_l0`, `state_heads.{i}.state_mean_layers.{0,2}`,
...) for two reasons: the checkpoint loads with strict=True, and the gradient
differential test in section 3 can compare parameter-by-parameter **by name**.

Every structural choice is quoted from the source it came from. The inference
path here is the one already bitwise-verified in R-11; the training path is new
and is what section 3 gates.

Faithfulness note (1b): the state loss is squared error on a REPARAMETERISED
SAMPLE, and there is no log-sigma term anywhere. For a sample s = mu + sigma*eps,

    E[(mu + sigma*eps - y)^2] = (mu - y)^2 + sigma^2

so the objective is minimised at sigma = 0 on its own, and the bound loss pushes
the same way. Variance collapse (C-10) is the optimum of this objective, not a
training accident. This is reproduced faithfully and NOT fixed in the main arm.
"""

import torch
import torch.nn as nn


class Memory(nn.Module):
    """rnn.py:33-47. Carries hidden state across calls; reset() clears it."""

    def __init__(self, input_dim, hidden_size, num_layers, rnn_type="gru"):
        super().__init__()
        cls = nn.GRU if rnn_type.lower() == "gru" else nn.LSTM
        self.rnn = cls(input_size=input_dim, hidden_size=hidden_size,
                       num_layers=num_layers, batch_first=True)
        self.hidden_states = None

    def forward(self, x):
        x, self.hidden_states = self.rnn(x, self.hidden_states)
        return x[:, -1]                                    # rnn.py:44

    def reset(self):
        self.hidden_states = None


class RNNBase(nn.Module):
    """rnn.py:5-27. Input is cat([normalised state, action], -1) -> 57."""

    def __init__(self, input_dim, hidden_size, num_layers, rnn_type="gru"):
        super().__init__()
        self.memory = Memory(input_dim, hidden_size, num_layers, rnn_type)

    def forward(self, x_state_batch, x_action_batch):
        return self.memory(torch.cat([x_state_batch, x_action_batch], dim=-1))

    def reset(self):
        self.memory.reset()


class MLPStateHead(nn.Module):
    """mlp.py:38-103."""

    def __init__(self, input_dim, state_dim, mean_shape, logstd_shape):
        super().__init__()
        self.state_dim = state_dim
        self.output_std = logstd_shape is not None

        def tower(shape):
            layers, c = [], input_dim
            for h in shape:
                layers += [nn.Linear(c, h), nn.ReLU()]      # mlp.py:56-57
                c = h
            layers.append(nn.Linear(shape[-1], state_dim))  # mlp.py:59, no activation
            return nn.Sequential(*layers)

        self.state_mean_layers = tower(mean_shape)
        if self.output_std:
            self.state_logstd_layers = tower(logstd_shape)
            # mlp.py:78-79 -- initialised to constant -5.0 and 0.0
            self.state_min_logstd = nn.Parameter(torch.ones(1, state_dim) * -5.0)
            self.state_log_delta_logstd = nn.Parameter(torch.ones(1, state_dim) * 0.0)

    def forward(self, x, x_state_batch):
        # mlp.py:88 -- RESIDUAL: the head predicts a delta on the last input state
        state_mean = self.state_mean_layers(x) + x_state_batch[:, -1]
        if not self.output_std:
            inf = -torch.inf * torch.ones(x.shape[0], self.state_dim, device=x.device)
            return state_mean, torch.exp(inf)
        state_logstd = self.state_logstd_layers(x)
        # mlp.py:91-93 -- double softplus clamp into [min, min + exp(log_delta)]
        self.state_max_logstd = self.state_min_logstd + torch.exp(self.state_log_delta_logstd)
        state_logstd = self.state_max_logstd - nn.functional.softplus(
            self.state_max_logstd - state_logstd)
        state_logstd = self.state_min_logstd + nn.functional.softplus(
            state_logstd - self.state_min_logstd)
        return state_mean, torch.exp(state_logstd)          # mlp.py:97

    def reset(self):
        pass


class MLPAuxiliaryHead(nn.Module):
    """mlp.py:106-181. Emits LOGITS; no output activation."""

    def __init__(self, input_dim, extension_dim, contact_dim, termination_dim,
                 extension_shape, contact_shape, termination_shape):
        super().__init__()
        self.extension_dim, self.contact_dim = extension_dim, contact_dim
        self.termination_dim = termination_dim

        def tower(shape, out):
            layers, c = [], input_dim
            for h in shape:
                layers += [nn.Linear(c, h), nn.ReLU()]
                c = h
            layers.append(nn.Linear(shape[-1], out))
            return nn.Sequential(*layers)

        if extension_dim > 0:
            self.extension_layers = tower(extension_shape, extension_dim)
        if contact_dim > 0:
            self.contact_layers = tower(contact_shape, contact_dim)
        if termination_dim > 0:
            self.termination_layers = tower(termination_shape, termination_dim)

    def forward(self, x, x_state_batch):
        e = self.extension_layers(x) if self.extension_dim > 0 else None
        c = self.contact_layers(x) if self.contact_dim > 0 else None
        t = self.termination_layers(x) if self.termination_dim > 0 else None
        return e, c, t

    def reset(self):
        pass


class RWMEnsemble(nn.Module):
    """
    From-scratch reimplementation of SystemDynamicsEnsemble for the `rnn` /
    `prediction_type == "single"` configuration, which is what
    anymal_d_flat_cfg.py selects and what the released checkpoint is.

    The `sequence` prediction type and the `mlp` base are NOT implemented:
    _create_base sets prediction_type = "single" on BOTH branches
    (system_dynamics.py:67,76), so no configuration in this repository can reach
    the `sequence` code paths. Reimplementing dead code would be untestable.
    """

    def __init__(self, state_dim, action_dim, extension_dim, contact_dim,
                 termination_dim, ensemble_size, history_horizon,
                 architecture_config):
        super().__init__()
        assert architecture_config["type"] == "rnn", "only the rnn base is implemented"
        self.state_dim, self.action_dim = state_dim, action_dim
        self.extension_dim, self.contact_dim = extension_dim, contact_dim
        self.termination_dim = termination_dim
        self.ensemble_size = ensemble_size
        self.history_horizon = history_horizon
        self.architecture_config = architecture_config
        self.prediction_type = "single"                     # system_dynamics.py:76

        ac = architecture_config
        h = ac["rnn_hidden_size"]
        mk_base = lambda: RNNBase(state_dim + action_dim, h, ac["rnn_num_layers"],
                                  ac["rnn_type"])
        self.state_base = mk_base()
        self.state_heads = nn.ModuleList([
            MLPStateHead(h, state_dim, ac["state_mean_shape"], ac["state_logstd_shape"])
            for _ in range(ensemble_size)])
        self.auxiliary_base = mk_base()
        self.auxiliary_heads = nn.ModuleList([
            MLPAuxiliaryHead(h, extension_dim, contact_dim, termination_dim,
                             ac["extension_shape"], ac["contact_shape"],
                             ac["termination_shape"])
            for _ in range(ensemble_size)])

    # ------------------------------------------------------------ inference
    def reset(self):
        self.state_base.reset()
        self.auxiliary_base.reset()

    def forward(self, x_state_batch, x_action_batch):
        """system_dynamics.py:83-127, model_ids=None branch."""
        base = self.state_base(x_state_batch, x_action_batch)
        means, stds = [], []
        for head in self.state_heads:
            m, s = head(base, x_state_batch)
            means.append(m.unsqueeze(0))
            stds.append(s.unsqueeze(0))
        means, stds = torch.cat(means, 0), torch.cat(stds, 0)

        abase = self.auxiliary_base(x_state_batch, x_action_batch)   # same 57-dim input
        contacts, terms = [], []
        for head in self.auxiliary_heads:
            _, c, t = head(abase, x_state_batch)
            contacts.append(c.unsqueeze(0) if c is not None else None)
            terms.append(t.unsqueeze(0) if t is not None else None)

        return (means.mean(0),                              # :114 ensemble mean
                stds.mean(0).sum(1),                        # :126 aleatoric
                means.std(0).sum(1) if self.ensemble_size > 1
                else torch.zeros(means.shape[1], device=means.device),  # :127 epistemic
                torch.cat(contacts, 0).mean(0) if self.contact_dim > 0 else None,
                torch.cat(terms, 0).mean(0) if self.termination_dim > 0 else None)

    @torch.no_grad()
    def rollout(self, state, action, start_step, action_offset=1):
        """
        model_training.py:126-133. First forecast step consumes the whole history,
        later steps a single timestep, hidden state carried throughout.

        action_offset=1 is the causal alignment (D-13, X-05); 0 reproduces the
        released evaluation code.
        """
        B, T, _ = state.shape
        pred = state.clone()
        self.reset()
        for i in range(start_step, T):
            if i > start_step:
                s_in = pred[:, i - 1:i]
                a_in = action[:, i - 1 + action_offset:i + action_offset]
            else:
                s_in = pred[:, i - start_step:i]
                a_in = action[:, i - start_step + action_offset:i + action_offset]
            if a_in.shape[1] != s_in.shape[1]:
                a_in = action[:, -s_in.shape[1]:]
            m, *_ = self.forward(s_in, a_in)
            pred[:, i] = m
        return pred

    # ------------------------------------------------------------- training
    def compute_regression_loss(self, mean, std, target):
        """
        system_dynamics.py:270-289, loss_type="mse" (the default; nothing in the
        repository ever passes "gaussian_nll").

        The SAMPLE enters the squared error, not the mean. Summed over the 45
        state dims, meaned over the batch. sequence_loss is identically zero for
        prediction_type == "single".
        """
        pred = torch.randn_like(mean, device=mean.device) * std + mean
        state_loss = torch.sum(torch.square(pred - target), dim=1).mean(dim=0)
        sequence_loss = torch.tensor(0.0, device=mean.device)
        return state_loss, sequence_loss

    @staticmethod
    def compute_bound_loss(head):
        """system_dynamics.py:301-302. Requires head.forward to have run."""
        return torch.mean(head.state_max_logstd) - torch.mean(head.state_min_logstd)

    def compute_state_loss(self, head, state_batch, action_batch, teacher_forcing=False):
        """
        system_dynamics.py:179-231.

        `teacher_forcing` is the ONLY difference between Step 5's two arms:

          False (Arm A, faithful)  the state branch consumes its own reparameterised
                                   sample, system_dynamics.py:216
          True  (Arm B)            it consumes the true next state -- exactly the regime
                                   the auxiliary branch already uses at
                                   system_dynamics.py:264

        Nothing else changes. The loss still computes squared error on a sample in both
        arms; the difference is the feedback, not the objective.
        """
        H = self.history_horizon
        forecast_horizon = state_batch.shape[1] - H
        x_state_batch = state_batch[:, :H]
        s_losses, q_losses, b_losses, k_losses = [], [], [], []

        for i in range(forecast_horizon):
            state_target = state_batch[:, H + i]                     # "single"
            if i > 0:
                x_action_batch = action_batch[:, H + i:H + i + 1]    # :196-197
            else:
                x_action_batch = action_batch[:, i + 1:H + i + 1]    # :200
            mean, std = head(self.state_base(x_state_batch, x_action_batch), x_state_batch)
            s, q = self.compute_regression_loss(mean, std, state_target)
            b = self.compute_bound_loss(head) if head.output_std \
                else torch.tensor(0.0, device=mean.device)
            k = torch.tensor(0.0, device=mean.device)                # kl: rssm only
            s_losses.append(s.unsqueeze(0)); q_losses.append(q.unsqueeze(0))
            b_losses.append(b.unsqueeze(0)); k_losses.append(k.unsqueeze(0))
            if teacher_forcing:
                # Arm B: the true next state, matching the auxiliary branch (:264)
                x_state_batch = state_batch[:, H + i:H + i + 1]
            else:
                # Arm A / reference: feed back a SAMPLE, single timestep (:216)
                x_state_batch = (torch.randn_like(mean, device=mean.device) * std + mean
                                 ).unsqueeze(1) if head.output_std else mean.unsqueeze(1)

        m = lambda L: torch.mean(torch.cat(L, dim=0), dim=0)
        return m(s_losses), m(q_losses), m(b_losses), m(k_losses)

    def compute_auxiliary_loss(self, head, state_batch, action_batch,
                               extension_batch, contact_batch, termination_batch):
        """
        system_dynamics.py:233-268.

        Note the asymmetry with compute_state_loss: this branch feeds back the
        TRUE state (:264, teacher forcing), not its own prediction.
        """
        H = self.history_horizon
        forecast_horizon = state_batch.shape[1] - H
        x_state_batch = state_batch[:, :H]
        e_losses, c_losses, t_losses = [], [], []
        dev = state_batch.device

        for i in range(forecast_horizon):
            c_target = contact_batch[:, H + i] if contact_batch is not None else None
            t_target = termination_batch[:, H + i] if termination_batch is not None else None
            if i > 0:
                x_action_batch = action_batch[:, H + i:H + i + 1]
            else:
                x_action_batch = action_batch[:, i + 1:H + i + 1]
            _, c_pred, t_pred = head(self.auxiliary_base(x_state_batch, x_action_batch),
                                     x_state_batch)
            e = torch.tensor(0.0, device=dev)                        # extension_dim = 0
            c = nn.BCEWithLogitsLoss()(c_pred, c_target) if self.contact_dim > 0 \
                else torch.tensor(0.0, device=dev)
            t = nn.BCEWithLogitsLoss()(t_pred, t_target) if self.termination_dim > 0 \
                else torch.tensor(0.0, device=dev)
            e_losses.append(e.unsqueeze(0)); c_losses.append(c.unsqueeze(0))
            t_losses.append(t.unsqueeze(0))
            x_state_batch = state_batch[:, H + i:H + i + 1]          # :264 TRUE state
        m = lambda L: torch.mean(torch.cat(L, dim=0), dim=0)
        return m(e_losses), m(c_losses), m(t_losses)

    def compute_loss(self, state_batch, action_batch, extension_batch,
                     contact_batch, termination_batch, bootstrap=False,
                     teacher_forcing=False):
        """system_dynamics.py:128-177. Per-member, then meaned over the ensemble."""
        acc = {k: [] for k in ("state", "sequence", "bound", "kl",
                               "extension", "contact", "termination")}
        for i in range(self.ensemble_size):
            if bootstrap:
                ids = torch.randint(0, state_batch.shape[0], (state_batch.shape[0],),
                                    device=state_batch.device)
            else:
                ids = torch.arange(0, state_batch.shape[0], device=state_batch.device)
            s, q, b, k = self.compute_state_loss(self.state_heads[i],
                                                 state_batch[ids], action_batch[ids],
                                                 teacher_forcing=teacher_forcing)
            e, c, t = self.compute_auxiliary_loss(
                self.auxiliary_heads[i], state_batch[ids], action_batch[ids],
                extension_batch[ids] if extension_batch is not None else None,
                contact_batch[ids] if contact_batch is not None else None,
                termination_batch[ids] if termination_batch is not None else None)
            for key, v in zip(acc, (s, q, b, k, e, c, t)):
                acc[key].append(v.unsqueeze(0))
        return tuple(torch.mean(torch.cat(acc[k], dim=0), dim=0) for k in
                     ("state", "sequence", "bound", "kl",
                      "extension", "contact", "termination"))

    # ------------------------------------------------------------ monitoring
    @torch.no_grad()
    def sigma_sq_sum(self, state_batch, action_batch):
        """
        Sum_d sigma_d^2 at the first forecast step, per Step 5.6 -- the analytic
        single-step floor of the sampled-MSE objective, since
        E[sum_d (mu_d + sigma_d*eps_d - y_d)^2] = sum_d (mu_d - y_d)^2 + sum_d sigma_d^2.
        """
        H = self.history_horizon
        out = []
        for head in self.state_heads:
            self.reset()
            _, std = head(self.state_base(state_batch[:, :H], action_batch[:, 1:H + 1]),
                          state_batch[:, :H])
            out.append(float((std ** 2).sum(-1).mean()))
        return float(sum(out) / len(out))

    @torch.no_grad()
    def collapse_stats(self):
        """1b collapse monitor: the width of the learned logstd interval."""
        d = torch.cat([h.state_log_delta_logstd.flatten() for h in self.state_heads])
        mn = torch.cat([h.state_min_logstd.flatten() for h in self.state_heads])
        return {"exp_log_delta_logstd_mean": float(torch.exp(d).mean()),
                "exp_min_logstd_mean": float(torch.exp(mn).mean()),
                "log_delta_logstd_mean": float(d.mean()),
                "min_logstd_mean": float(mn.mean())}


def build_from_config(cfg, ensemble_size=None, state_dim=45, action_dim=12):
    return RWMEnsemble(
        state_dim=state_dim, action_dim=action_dim, extension_dim=0,
        contact_dim=cfg["contact_dim"], termination_dim=cfg["termination_dim"],
        ensemble_size=ensemble_size or cfg["ensemble_size"],
        history_horizon=cfg["history_horizon"],
        architecture_config=cfg["architecture_config"])


TOTAL_WEIGHT_KEYS = ("state", "sequence", "bound", "kl",
                     "extension", "contact", "termination")


def weighted_total(terms, weights):
    """model_training.py:66-73."""
    return sum(weights[k] * v for k, v in zip(TOTAL_WEIGHT_KEYS, terms))
