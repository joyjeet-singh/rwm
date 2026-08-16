# Step 4 / 1a — the reference loss assembly, READ AND REPORT

Everything below is read from `rsl_rl_rwm/rsl_rl/modules/system_dynamics.py` at commit
`18eebcdd`, with `mlp.py` for the head internals. Nothing is inferred.

Configuration in force throughout: `architecture_config["type"] == "rnn"`,
`prediction_type == "single"`, `history_horizon = 32`, `forecast_horizon = 8`,
`ensemble_size = 5`, `extension_dim = 0`, `contact_dim = 8`, `termination_dim = 1`.

---

## 1. Exact slicing of `x_state_batch`, `x_action_batch` and `state_target`

`compute_state_loss`, lines 179–231. Before the loop:

```python
forecast_horizon = state_batch.shape[1] - self.history_horizon      # 40 - 32 = 8
x_state_batch    = state_batch[:, :self.history_horizon]            # (B, 32, 45)
```

Inside the loop over `i in range(8)`:

| | `prediction_type == "single"` (in force) | `prediction_type == "sequence"` |
|---|---|---|
| `state_target` | `state_batch[:, 32+i]` → `(B, 45)` | `state_batch[:, i+1 : 32+i+1]` → `(B, 32, 45)` |
| `x_action_batch`, `i == 0` | `action_batch[:, 1 : 33]` | same |
| `x_action_batch`, `i > 0` | `action_batch[:, 32+i : 32+i+1]` | same, and `state_target = state_target[:, [-1]]` |
| `x_state_batch`, `i == 0` | `state_batch[:, :32]` | same |
| `x_state_batch`, `i > 0` | the previous step's **sample**, `(B, 1, 45)` | same |

The state feedback (line 216, `rnn`/`rssm` branch):

```python
x_state_batch = (torch.randn_like(state_mean_pred) * state_std_pred
                 + state_mean_pred).unsqueeze(1)
```

so from `i = 1` onward the trunk consumes a **single timestep** — its own reparameterised
sample — with the GRU hidden state carrying the history. The `mlp` branch instead shifts a
window: `cat([x_state_batch[:, 1:], sample], dim=1)`.

**Note the action indexing.** At `i = 0` the pairing is `state_batch[:, :32]` with
`action_batch[:, 1:33]`, i.e. `(s[t], a[t+1]) → s[t+1]`. Under `D-13` (row *t* holds the
action that produced state *t*) this is the **causal** pairing, and it is what our trainer
uses. It differs from `model_training.py:131-132`, which is the evaluation path.

**`sequence` is dead code.** `_create_base` sets `prediction_type = "single"` on *both* the
`mlp` (line 67) and `rnn` (line 76) branches, so no configuration in this repository can
reach any `sequence` path. Our reimplementation does not implement it, since it is
untestable against the reference.

---

## 2. How `state_loss` and `sequence_loss` split

They do not split, in this configuration. In `compute_regression_loss`
(lines 270–289), the `sequence_loss` branch is guarded by
`if self.prediction_type == "sequence"`, and the `else` sets

```python
sequence_loss = torch.tensor(0.0, device=self.device)
```

So with `prediction_type == "single"`, **`sequence_loss` is identically zero at every
forecast step**, and all eight steps contribute to `state_loss`. Its configured weight of
1.0 is inert.

Had `sequence` been reachable, the split would be: the last timestep of the predicted
sequence → `state_loss`, all earlier timesteps (flattened over batch and time) →
`sequence_loss`.

Both are reduced the same way, an unweighted mean over the 8 forecast steps
(lines 227–231) and then an unweighted mean over the 5 ensemble members
(lines 170–176). **There is no forecast decay factor** — see `C-09`.

---

## 3. `compute_regression_loss` — the sample enters the squared error

Lines 270–289, `loss_type="mse"`, which is the default and is never overridden anywhere in
either repository:

```python
state_pred = torch.randn_like(state_mean_pred) * state_std_pred + state_mean_pred
state_loss = torch.sum(torch.square(state_pred - state_target), dim=1).mean(dim=0)
```

So it is the **reparameterised sample**, not the mean, that enters the squared error;
summed over the 45 state dimensions, then meaned over the batch.

A `gaussian_nll` branch exists (lines 291–305) using `nn.GaussianNLLLoss`, but nothing
calls it. This matters for `C-10`: a Gaussian NLL carries a `log σ` term that penalises
shrinking σ, and the MSE-on-a-sample form does not. That absence is what makes the variance
collapse the optimum rather than an accident.

---

## 4. `compute_bound_loss`

Lines 301–302:

```python
def compute_bound_loss(self, head):
    return torch.mean(head.state_max_logstd) - torch.mean(head.state_min_logstd)
```

`state_max_logstd` is not a parameter. It is set as a side effect of `MLPStateHead.forward`
(`mlp.py:91`) as `state_min_logstd + exp(state_log_delta_logstd)`, so `compute_bound_loss`
is only valid after a forward pass has run for that head.

Substituting, the loss is

```
mean(min_logstd + exp(log_delta_logstd)) - mean(min_logstd) = mean(exp(log_delta_logstd))
```

**`state_min_logstd` cancels algebraically and therefore receives no gradient from this
term.** Confirmed empirically in the gradient differential test: under zero-noise sampling,
`state_min_logstd` is one of exactly 25 tensors with an identically zero gradient (the other
20 being the five heads' `state_logstd_layers`). This sharpens the `C-10` mechanism — see
`C-11`.

The term is recomputed identically at all 8 forecast steps and then averaged, so it
contributes 8 identical values.

---

## 5. Contact and termination losses, and their targets

`compute_auxiliary_loss`, lines 233–268, with the loss bodies at 311–324:

```python
contact_target     = contact_batch[:, self.history_horizon + i]        # (B, 8)
termination_target = termination_batch[:, self.history_horizon + i]    # (B, 1)
...
nn.BCEWithLogitsLoss()(contact_pred, contact_target)
nn.BCEWithLogitsLoss()(termination_pred, termination_target)
```

Both are `BCEWithLogitsLoss` against the raw 0/1 columns at forecast step `i` — columns
57–64 for contacts, column 65 for termination. The heads emit **logits**; there is no
output activation (`mlp.py:166-168`). Both are averaged over the 8 forecast steps and then
over the 5 members.

Because column 65 is identically zero (`D-03`), the termination target is all-zero and the
term collapses to driving its logits to −∞. That is `X-04`.

---

## 6. Does the auxiliary branch receive gradient from the state loss?

**No.** The two branches are structurally disjoint:

- `compute_state_loss` uses `self.state_base` and `self.state_heads[i]` (line 204)
- `compute_auxiliary_loss` uses `self.auxiliary_base` and `self.auxiliary_heads[i]` (line 253)

They are separate `RNNBase` instances (`C-03`), so no gradient path connects the state loss
to the auxiliary parameters or vice versa. The only coupling is that both consume the same
input tensors.

There is one further asymmetry worth recording, which the brief did not ask about but which
matters for reimplementation: **the auxiliary branch is teacher-forced.** Its feedback at
line 264 is

```python
x_state_batch = state_batch[:, self.history_horizon + i : self.history_horizon + i + 1]
```

— the **true** next state, whereas the state branch feeds back its own sample (line 216).
So the contact and termination heads are never trained on the model's own rollout error,
while the state head is. Reproduced faithfully.

---

## 7. What `freeze_auxiliary` does

Two things.

At construction (`_init_networks`, lines 56–61):

```python
if self.freeze_auxiliary:
    for param in self.auxiliary_base.parameters():
        param.requires_grad = False
    for head in self.auxiliary_heads:
        for param in head.parameters():
            param.requires_grad = False
```

and on every `train()` call (lines 343–348) it forces the auxiliary modules back into eval
mode, so a later `model.train()` cannot silently re-enable them.

It does **not** remove the auxiliary loss terms from the total — they are still computed and
still added, they simply cannot move any parameter. The config sets it to `False`
by default, so it is inactive in the released setup.
