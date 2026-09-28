"""
The MLP baseline (rules M-75, M-76). It is the upstream's own MLP base, rsl_rl_rwm
rsl_rl/modules/architectures/mlp.py:5-29 at 18eebcdd, rebuilt here:
  input  the last H (state, action) rows, concatenated per row and flattened
         (mlp.py:27: torch.cat([x_state, x_action], -1).flatten(1, 2));
  layers Linear -> ReLU for each width in base_shape (mlp.py:16-23).
The original's Table S7 gives base_shape [256, 256] with ReLU, which is also the upstream
config's default MLP (robotic_world_model_lite scripts/configs/base_cfg.py:61-63).
The state head, loss and regimes are src/baselines/common.py's.
"""
import torch
import torch.nn as nn

from baselines.common import ACTION_DIM, STATE_DIM, WindowModel


class MLPBaseline(WindowModel):
    def __init__(self, history, cfg, base_shape=(256, 256)):
        super().__init__(history, cfg, base_shape[-1])
        layers, c = [], history * (STATE_DIM + ACTION_DIM)
        for w in base_shape:
            layers += [nn.Linear(c, w), nn.ReLU()]
            c = w
        self.layers = nn.Sequential(*layers)
        self.base_shape = list(base_shape)

    def encode(self, x_state, x_action):
        return self.layers(torch.cat([x_state, x_action], dim=-1).flatten(1, 2))
