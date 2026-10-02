"""
The RSSM baseline (rules M-75, M-76). A recurrent state-space model: a deterministic GRU
state h_t, a stochastic latent z_t with a prior p(z_t | h_t) and a posterior
q(z_t | h_t, o_t), and the RWM state head decoding the next state from (h_t, z_t).

    h_t = GRU(h_{t-1}, f([z_{t-1}, a_t]))        h_{-1} = 0, z_{-1} = 0
    prior      p(z_t | h_t)                       posterior  q(z_t | h_t, e(o_t))
    decode     o_t = o_{t-1} + delta(h_t, z_t)    (RWM's residual head; sigma bounded as RWM's)

Actions are causal as everywhere else: row t's action produced row t's state, so h_t reads
a_t. The decode's residual base is the previous state: true while filtering, the model's own
prediction while forecasting. Row 0 has no previous state, so it contributes a KL term and
no reconstruction.

TWO LATENT TYPES (docs/presubmission/BASELINE_SPECS.md holds the citations):
  "categorical"  the original's Table S7: GRU of 256 units, 2 layers, latent dimension 64,
                 categorical prior, 32 categories -- read, with DreamerV2's own naming
                 ("discrete latent dimensions" x "classes"), as 64 categorical variables of
                 32 classes each. Straight-through sampling, ELU activations, KL balancing
                 alpha = 0.8, no free nats, KL scale 0.1 (DreamerV2 Table; the upstream
                 config's own kl weight is also 0.1).
  "gaussian"     PLAN S2b's parameter-matched variant: diagonal Gaussian latent of 30 dims,
                 ReLU, 3 free nats, no KL balancing and no KL scaling (PlaNet, p. 12).

TRAINING OBJECTIVES, by regime, over a window of H history and F forecast rows:
  tf  the RSSM's own teacher-forced objective (rule M-75): the posterior filters every row
      of the window; the decoder reconstructs each row from its posterior latent; plus
      the KL term on every row.
  ar  rule M-76: the posterior filters the H history rows (KL term there); the prior then
      rolls open-loop over the F forecast rows, feeding back its own latent samples and,
      as the residual base, its own sampled state; the loss is RWM's sampled squared error
      on those decoded forecasts.
ROLLOUT (both): filter the history with the posterior's mode, then forecast with the
prior's mode, feeding back the predicted mean -- the deterministic analogue of RWM's
rollout, which feeds back its mean.
"""
import torch
import torch.nn as nn
import torch.nn.functional as Fn

from baselines.common import ACTION_DIM, STATE_DIM, bound_loss, regression_loss, state_head


class LNGRUCell(nn.Module):
    """DreamerV2's layer-normalised GRU cell (rule X1, variant V2), transcribed from danijar/dreamerv2
    common/nets.py:317-347 at 07d906e9: one dense layer with bias on [input, state] to 3 x size; layer
    normalisation over all 3 x size parts with Keras's defaults (epsilon 1e-3, learned scale and centre;
    keras v2.6.0 layer_normalization.py:151-155); split into reset, candidate, update; reset = sigmoid;
    candidate = tanh(reset * candidate); update = sigmoid(update - 1); h' = update * candidate +
    (1 - update) * h. Initialised with PyTorch's defaults, like every other layer of this RSSM."""

    def __init__(self, inp, size, update_bias=-1.0):
        super().__init__()
        self.size, self.update_bias = size, update_bias
        self.layer = nn.Linear(inp + size, 3 * size, bias=True)
        self.norm = nn.LayerNorm(3 * size, eps=1e-3)

    def forward(self, x, h):
        parts = self.norm(self.layer(torch.cat([x, h], -1)))
        reset, cand, update = parts.split(self.size, -1)
        reset = torch.sigmoid(reset)
        cand = torch.tanh(reset * cand)
        update = torch.sigmoid(update + self.update_bias)
        return update * cand + (1 - update) * h


class LNGRU(nn.Module):
    """A stack of LNGRUCells behind nn.GRU's batch_first single-step interface: input (B, 1, in), state
    (layers, B, size) -> (output (B, 1, size), new state). Layer l+1 reads layer l's new state, as in
    nn.GRU without dropout."""

    def __init__(self, inp, size, num_layers):
        super().__init__()
        self.cells = nn.ModuleList([LNGRUCell(inp if i == 0 else size, size) for i in range(num_layers)])

    def forward(self, x, hstate):
        h_in, new = x[:, 0], []
        for i, cell in enumerate(self.cells):
            h_in = cell(h_in, hstate[i])
            new.append(h_in)
        return h_in.unsqueeze(1), torch.stack(new)


class RSSMBaseline(nn.Module):
    def __init__(self, history, cfg, latent="categorical", deter=256, hidden=256,
                 gru_layers=2, n_vars=64, n_classes=32, stoch=30, act="elu",
                 kl_balance=0.8, free_nats=0.0, kl_scale=0.1, min_std=0.1, gru_norm=False):
        super().__init__()
        self.history, self.latent = history, latent
        self.kl_balance, self.free_nats, self.kl_scale, self.min_std = \
            kl_balance, free_nats, kl_scale, min_std
        A = nn.ELU if act == "elu" else nn.ReLU
        if latent == "categorical":
            self.n_vars, self.n_classes = n_vars, n_classes
            self.z_dim = n_vars * n_classes
            n_stats = self.z_dim
        elif latent == "gaussian":
            self.z_dim = stoch
            n_stats = 2 * stoch
        else:
            raise ValueError(latent)
        self.encoder = nn.Sequential(nn.Linear(STATE_DIM, hidden), A())
        self.img_in = nn.Sequential(nn.Linear(self.z_dim + ACTION_DIM, hidden), A())
        # gru_norm: rule X1's variant V2, DreamerV2's layer-normalised GRU cell; off for every rule-M-75/M-76 model
        self.gru = (LNGRU(hidden, deter, gru_layers) if gru_norm
                    else nn.GRU(hidden, deter, num_layers=gru_layers, batch_first=True))
        self.prior_net = nn.Sequential(nn.Linear(deter, hidden), A(), nn.Linear(hidden, n_stats))
        self.post_net = nn.Sequential(nn.Linear(deter + hidden, hidden), A(),
                                      nn.Linear(hidden, n_stats))
        self.head = state_head(deter + self.z_dim, cfg)
        self.gru_layers, self.deter = gru_layers, deter
        self.spec = {"latent": latent, "deter": deter, "hidden": hidden, "gru_layers": gru_layers,
                     "z_dim": self.z_dim, "activation": act, "kl_balance": kl_balance,
                     "free_nats": free_nats, "kl_scale": kl_scale, **({"gru_norm": True} if gru_norm else {}),
                     **({"n_vars": n_vars, "n_classes": n_classes} if latent == "categorical"
                        else {"stoch": stoch, "min_std": min_std})}

    def reset(self):
        pass

    # ---------------------------------------------------------------- latents
    def _dist(self, stats):
        if self.latent == "categorical":
            return stats.view(stats.shape[0], self.n_vars, self.n_classes)   # logits
        mean, raw = stats.chunk(2, dim=-1)
        return mean, Fn.softplus(raw) + self.min_std

    def _sample(self, d, mode=False):
        if self.latent == "categorical":
            probs = torch.softmax(d, dim=-1)
            if mode:
                idx = probs.argmax(-1)
            else:
                idx = torch.multinomial(probs.reshape(-1, self.n_classes), 1).view(probs.shape[:-1])
            onehot = Fn.one_hot(idx, self.n_classes).to(probs.dtype)
            return (onehot + probs - probs.detach()).flatten(1)       # straight-through
        mean, std = d
        return mean if mode else mean + std * torch.randn_like(std)

    def _kl(self, post, prior):
        """Per-sample KL(post || prior), with this latent type's balancing and free nats."""
        if self.latent == "categorical":
            def kl(lp, lq):   # KL(p || q) from logits, summed over classes and variables
                p = torch.softmax(lp, -1)
                return (p * (torch.log_softmax(lp, -1) - torch.log_softmax(lq, -1))).sum((-1, -2))
            a = self.kl_balance
            if a is None:     # no balancing (rule X1, variant V1): the plain KL, gradients to both sides
                k = kl(post, prior)
            else:
                k = a * kl(post.detach(), prior) + (1 - a) * kl(post, prior.detach())
        else:
            (m1, s1), (m2, s2) = post, prior
            k = (torch.log(s2 / s1) + (s1 ** 2 + (m1 - m2) ** 2) / (2 * s2 ** 2) - 0.5).sum(-1)
        return torch.clamp(k, min=self.free_nats) if self.free_nats > 0 else k

    # ---------------------------------------------------------------- one step
    def _transition(self, hstate, z_prev, a_t):
        out, hstate = self.gru(self.img_in(torch.cat([z_prev, a_t], -1)).unsqueeze(1), hstate)
        h = out[:, 0]
        return h, hstate, self._dist(self.prior_net(h))

    def _posterior(self, h, o_t):
        return self._dist(self.post_net(torch.cat([h, self.encoder(o_t)], -1)))

    def _init(self, batch, device):
        return (torch.zeros(self.gru_layers, batch, self.deter, device=device),
                torch.zeros(batch, self.z_dim, device=device))

    def _decode(self, h, z, prev):
        return self.head(torch.cat([h, z], -1), prev.unsqueeze(1))

    # ---------------------------------------------------------------- training
    def compute_state_loss(self, state_batch, action_batch, regime):
        """(state, bound, kl) losses, each meaned over the rows it covers."""
        B, T, _ = state_batch.shape
        H = self.history
        hstate, z = self._init(B, state_batch.device)
        s_l, b_l, k_l = [], [], []
        last = T if regime == "tf" else H          # rows the posterior filters
        for t in range(last):
            h, hstate, prior = self._transition(hstate, z, action_batch[:, t])
            post = self._posterior(h, state_batch[:, t])
            z = self._sample(post)
            k_l.append(self._kl(post, prior).mean().unsqueeze(0))
            if regime == "tf" and t >= 1:
                mean, std = self._decode(h, z, state_batch[:, t - 1])
                s_l.append(regression_loss(mean, std, state_batch[:, t]).unsqueeze(0))
                b_l.append(bound_loss(self.head).unsqueeze(0))
        if regime == "ar":
            prev = state_batch[:, H - 1]
            for t in range(H, T):
                h, hstate, prior = self._transition(hstate, z, action_batch[:, t])
                z = self._sample(prior)
                mean, std = self._decode(h, z, prev)
                s_l.append(regression_loss(mean, std, state_batch[:, t]).unsqueeze(0))
                b_l.append(bound_loss(self.head).unsqueeze(0))
                prev = torch.randn_like(mean) * std + mean
        elif regime != "tf":
            raise ValueError(regime)
        m = lambda L: torch.cat(L).mean()
        return m(s_l), m(b_l), m(k_l)

    # ---------------------------------------------------------------- rollout
    @torch.no_grad()
    def rollout(self, state, action, start_step, action_offset=1):
        assert action_offset == 1, "the baselines are evaluated with the causal alignment only"
        assert start_step == self.history, "the RSSM filters exactly its history rows"
        B, T, _ = state.shape
        pred = state.clone()
        hstate, z = self._init(B, state.device)
        for t in range(start_step):
            h, hstate, _ = self._transition(hstate, z, action[:, t])
            z = self._sample(self._posterior(h, state[:, t]), mode=True)
        prev = state[:, start_step - 1]
        for t in range(start_step, T):
            h, hstate, prior = self._transition(hstate, z, action[:, t])
            z = self._sample(prior, mode=True)
            mean, _ = self._decode(h, z, prev)
            pred[:, t] = mean
            prev = mean
        return pred
