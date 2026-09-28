"""
The transformer baseline (rules M-75, M-76). The original's Table S7 (2501.10100v1 p. 15):
type decoder, dimension 64, 8 heads, 2 layers, context length 32, sinusoidal positional
encoding. Nothing else about it is stated (docs/presubmission/BASELINE_SPECS.md).

A decoder-only (causal) transformer over the last H rows. Each row is one token:
(state, action) -> Linear -> dimension d, plus a position code for its place in the
window. Causal self-attention, pre-norm layers (nn.TransformerEncoderLayer with
norm_first=True and a causal mask is a decoder-only block), a final LayerNorm, and the
state head reads the LAST token. The context is capped at H = 32: in rollout the window
slides, appending each prediction and dropping the oldest row, so positions always run
0..H-1 exactly as in training.

positions="sinusoidal" is Table S7's (Vaswani et al. 2017, sine and cosine of
geometrically spaced frequencies); positions="learned" is PLAN S2b's, for the
parameter-matched variant only.
"""
import math

import torch
import torch.nn as nn

from baselines.common import ACTION_DIM, STATE_DIM, WindowModel


def sinusoidal(length, d):
    pos = torch.arange(length, dtype=torch.float32)[:, None]
    div = torch.exp(torch.arange(0, d, 2, dtype=torch.float32) * (-math.log(10000.0) / d))
    pe = torch.zeros(length, d)
    pe[:, 0::2] = torch.sin(pos * div)
    pe[:, 1::2] = torch.cos(pos * div)
    return pe


class TransformerBaseline(WindowModel):
    def __init__(self, history, cfg, d_model=64, n_heads=8, n_layers=2, ff_mult=4,
                 positions="sinusoidal"):
        super().__init__(history, cfg, d_model)
        self.embed = nn.Linear(STATE_DIM + ACTION_DIM, d_model)
        if positions == "sinusoidal":
            self.register_buffer("pos", sinusoidal(history, d_model), persistent=False)
        elif positions == "learned":
            self.pos = nn.Parameter(torch.zeros(history, d_model))
            nn.init.normal_(self.pos, std=0.02)
        else:
            raise ValueError(positions)
        layer = nn.TransformerEncoderLayer(d_model, n_heads, dim_feedforward=ff_mult * d_model,
                                           dropout=0.0, activation="relu", batch_first=True,
                                           norm_first=True)
        self.blocks = nn.TransformerEncoder(layer, n_layers, enable_nested_tensor=False)
        self.norm = nn.LayerNorm(d_model)
        self.register_buffer("mask", nn.Transformer.generate_square_subsequent_mask(history),
                             persistent=False)
        self.spec = {"d_model": d_model, "n_heads": n_heads, "n_layers": n_layers,
                     "dim_feedforward": ff_mult * d_model, "positions": positions}

    def encode(self, x_state, x_action):
        h = self.embed(torch.cat([x_state, x_action], dim=-1)) + self.pos
        h = self.blocks(h, mask=self.mask, is_causal=True)
        return self.norm(h[:, -1])
