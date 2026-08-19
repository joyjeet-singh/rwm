"""
Step 4 / 2 -- the trainer: data pipeline, hyperparameters, train step.

Data pipeline (2a):
  * 40-step windows (32 history + 8 forecast), TRAINING EPISODES ONLY,
    episode-aware, no boundary crossings -> 7,687 windows on the seed-0 split.
  * Causal alignment per D-13 / X-05. Note this is achieved by using the
    reference's own TRAINING slicing (system_dynamics.py:196-200), which pairs
    (s[t], a[t+1]) -> s[t+1]. Our deviation is from the reference's EVALUATION
    code, not its training code.
  * Normalisation imported from the config; actions left unnormalised (C-07).

Hyperparameters (2b) are read from base_cfg.py / anymal_d_flat_cfg.py, never
retyped. See report_hyperparameters().
"""

import numpy as np
import torch

import rwm_data as R
import rwm_model as M

WINDOW = 40


class WindowDataset:
    """40-step windows from the training episodes, held entirely in memory."""

    def __init__(self, data, episode_id, episodes, cfg, window=WINDOW):
        starts = R.valid_window_starts(episode_id, window)
        self.starts = np.array([s for s in starts if episode_id[s] in episodes])
        assert len(self.starts) > 0
        idx = self.starts[:, None] + np.arange(window)[None, :]
        raw = data[idx]
        self.state = torch.as_tensor(
            R.normalise_state(raw[:, :, R.STATE_COLS], cfg["state_data_mean"],
                              cfg["state_data_std"]), dtype=torch.float32)
        self.action = torch.as_tensor(raw[:, :, R.ACTION_COLS], dtype=torch.float32)
        self.contact = torch.as_tensor(raw[:, :, R.CONTACTS], dtype=torch.float32)
        self.termination = torch.as_tensor(raw[:, :, [R.TERMINATION]], dtype=torch.float32)
        self.extension = torch.zeros(len(self.starts), window, 0)
        self.episodes = sorted(set(episode_id[self.starts].tolist()))
        # every window must lie inside one episode
        for s in self.starts:
            seg = episode_id[s:s + window]
            assert seg[0] >= 0 and np.all(seg == seg[0])

    def __len__(self):
        return len(self.starts)

    def batch(self, idx):
        return (self.state[idx], self.action[idx], self.extension[idx],
                self.contact[idx], self.termination[idx])

    def sample(self, batch_size, generator):
        idx = torch.randint(0, len(self), (batch_size,), generator=generator)
        return self.batch(idx)


def make_optimizer(model, cfg):
    """Adam with the config's learning rate and weight decay (ModelOptimizerConfig)."""
    return torch.optim.Adam(model.parameters(), lr=cfg["learning_rate"],
                            weight_decay=cfg["weight_decay"])


def train_step(model, optimizer, batch, weights):
    """One optimisation step. Returns the seven raw terms plus the weighted total."""
    state, action, ext, contact, term = batch
    model.reset()
    optimizer.zero_grad(set_to_none=True)
    terms = model.compute_loss(state, action, ext, contact, term)
    total = M.weighted_total(terms, weights)
    total.backward()
    optimizer.step()
    return [float(t) for t in terms], float(total)


def report_hyperparameters(cfg):
    """
    2b -- every value imported, none retyped. Paper Table S7 differences flagged.
    """
    rows = [
        ("history_horizon", cfg["history_horizon"], ""),
        ("forecast_horizon", cfg["forecast_horizon"], ""),
        ("ensemble_size", cfg["ensemble_size"], ""),
        ("rnn_type", cfg["architecture_config"]["rnn_type"], ""),
        ("rnn_num_layers", cfg["architecture_config"]["rnn_num_layers"], ""),
        ("rnn_hidden_size", cfg["architecture_config"]["rnn_hidden_size"], ""),
        ("state_mean_shape", cfg["architecture_config"]["state_mean_shape"], ""),
        ("state_logstd_shape", cfg["architecture_config"]["state_logstd_shape"], ""),
        ("contact_shape", cfg["architecture_config"]["contact_shape"], ""),
        ("termination_shape", cfg["architecture_config"]["termination_shape"], ""),
        ("batch_size", cfg["batch_size"], ""),
        ("max_iterations", cfg["max_iterations"],
         "paper Table S7 states 2500 -- KNOWN DIFFERENCE"),
        ("learning_rate", cfg["learning_rate"], ""),
        ("weight_decay", cfg["weight_decay"], ""),
        ("save_interval", cfg["save_interval"], ""),
        ("loss weight state", cfg["loss_weights"]["state"], ""),
        ("loss weight sequence", cfg["loss_weights"]["sequence"],
         "inert: sequence_loss is identically 0 for prediction_type='single'"),
        ("loss weight bound", cfg["loss_weights"]["bound"], "drives the C-10 collapse"),
        ("loss weight kl", cfg["loss_weights"]["kl"], "inert: rssm only"),
        ("loss weight extension", cfg["loss_weights"]["extension"],
         "inert: extension_dim = 0"),
        ("loss weight contact", cfg["loss_weights"]["contact"], ""),
        ("loss weight termination", cfg["loss_weights"]["termination"],
         "target is all-zero (D-03/X-04)"),
        ("forecast decay alpha", "ABSENT", "paper specifies one; code has none (C-09)"),
    ]
    print(f"  {'hyperparameter':<26s} {'value':<22s} note")
    for k, v, note in rows:
        print(f"  {k:<26s} {str(v):<22s} {note}")
    return {k: v for k, v, _ in rows}


# --------------------------------------------------------------------------
# Task 4 -- the contamination arm (O-06)
# --------------------------------------------------------------------------
def splice_window_starts(episode_id, train_episodes, window=WINDOW):
    """
    Windows straddling a boundary between two CONSECUTIVE TRAINING episodes.

    The reference builder admits all 352 straddling windows because column 65 is
    identically zero (B-01). Reproducing that naively here would leak: 4 of the 9
    boundaries touch a held-out episode. Only boundaries whose BOTH sides are
    training episodes are included -- 2->3, 3->4, 4->5, 5->6, 6->7 -- giving
    5 x (window-1) = 195 windows.
    """
    starts = []
    for b in R.RESET_ROWS:
        if b >= len(episode_id) or b == 0:
            continue
        if episode_id[b - 1] in train_episodes and episode_id[b] in train_episodes:
            for s in range(b - window + 1, b):
                if s >= 0 and s + window <= len(episode_id):
                    starts.append(s)
    return sorted(starts)


class ContaminatedWindowDataset(WindowDataset):
    """The clean training windows PLUS the 195 within-training splices."""

    def __init__(self, data, episode_id, episodes, cfg, window=WINDOW):
        super().__init__(data, episode_id, episodes, cfg, window)
        splices = splice_window_starts(episode_id, set(episodes), window)
        self.n_clean, self.n_splice = len(self.starts), len(splices)
        idx = np.asarray(splices)[:, None] + np.arange(window)[None, :]
        touched = set(idx.flatten().tolist())
        held = {int(r) for r in np.flatnonzero(~np.isin(episode_id, list(episodes)))}
        assert not (touched & held), (
            f"LEAK: {len(touched & held)} held-out rows appear in the splice windows")
        raw = data[idx]
        self.starts = np.concatenate([self.starts, np.asarray(splices)])
        self.state = torch.cat([self.state, torch.as_tensor(
            R.normalise_state(raw[:, :, R.STATE_COLS], cfg["state_data_mean"],
                              cfg["state_data_std"]), dtype=torch.float32)])
        self.action = torch.cat([self.action, torch.as_tensor(
            raw[:, :, R.ACTION_COLS], dtype=torch.float32)])
        self.contact = torch.cat([self.contact, torch.as_tensor(
            raw[:, :, R.CONTACTS], dtype=torch.float32)])
        self.termination = torch.cat([self.termination, torch.as_tensor(
            raw[:, :, [R.TERMINATION]], dtype=torch.float32)])
        self.extension = torch.zeros(len(self.starts), window, 0)


class DuplicatedWindowDataset(WindowDataset):
    """
    Task 3's control for R-47: the same WINDOW COUNT as the contaminated arm, with no
    impossible transitions.

    The contaminated arm added 195 splice windows, taking 7,687 to 7,882, and scored
    slightly better on held-out data. The objection is that it also had 2.5% more
    training windows. This arm adds 195 *clean* windows instead -- chosen at random and
    duplicated -- so the count matches exactly and the only difference from the
    contaminated arm is whether the extra windows cross an episode boundary.

    The duplicated set is drawn from the TRAINING seed, so the three seeds average over
    which windows get duplicated rather than depending on one draw. The contaminated
    arm's extra set is fixed by construction (there are only 195 splices), so the control
    carries selection variance the contaminated arm does not -- making it the
    conservative side of the comparison.
    """

    def __init__(self, data, episode_id, episodes, cfg, window=WINDOW, n_extra=195, seed=0):
        super().__init__(data, episode_id, episodes, cfg, window)
        self.n_clean = len(self.starts)
        self.duplication_seed = 10_000 + seed
        rng = np.random.default_rng(self.duplication_seed)
        dup = rng.choice(len(self.starts), size=n_extra, replace=False)
        self.n_dup = int(n_extra)
        self.duplicated_window_starts = sorted(int(x) for x in self.starts[dup])
        self.starts = np.concatenate([self.starts, self.starts[dup]])
        for attr in ("state", "action", "contact", "termination"):
            t = getattr(self, attr)
            setattr(self, attr, torch.cat([t, t[dup]]))
        self.extension = torch.zeros(len(self.starts), window, 0)
