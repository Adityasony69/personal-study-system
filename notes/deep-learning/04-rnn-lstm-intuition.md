# RNN / LSTM Intuition

**Use case:** data where order matters: sensor readings, stock-like series, text, logs, anything that is a sequence.

## The idea in plain English

A normal network sees all inputs at once and forgets everything after. An **RNN (Recurrent Neural Network)** reads a sequence one step at a time and carries a **hidden state**, a running summary of what it has seen so far.

```
step 1 -> state1 -> step 2 -> state2 -> step 3 -> state3 -> prediction
```

Think of reading a sentence and keeping a mental note of the story so far.

**The problem:** a plain RNN has a short memory. When learning, the error signal gets squashed as it travels back through many steps (the *vanishing gradient* problem), so it forgets things from long ago.

**LSTM (Long Short-Term Memory)** fixes this by adding a protected memory lane (the *cell state*) with **gates** that learn what to forget, what to write and what to output. **GRU** is a lighter cousin that works about as well.

## Code: predict the next value of a noisy sine wave

Given the last 20 readings, predict the next one. The split is **by time** (train on the first 80%, test on the last 20%), as you must always do for time series.

```python
import torch, torch.nn as nn, numpy as np
torch.manual_seed(0)
t = np.arange(0, 100, 0.1)
series = np.sin(t) + np.random.default_rng(0).normal(0, 0.05, len(t))
L = 20
Xs = np.stack([series[i:i + L] for i in range(len(series) - L)])
ys = series[L:]
split = int(0.8 * len(Xs))
Xtr, Xte = torch.tensor(Xs[:split], dtype=torch.float32).unsqueeze(-1), torch.tensor(Xs[split:], dtype=torch.float32).unsqueeze(-1)
ytr, yte = torch.tensor(ys[:split], dtype=torch.float32), torch.tensor(ys[split:], dtype=torch.float32)

class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=32, batch_first=True)
        self.head = nn.Linear(32, 1)
    def forward(self, x):
        out, (h, c) = self.lstm(x)            # h = the "memory" after reading the whole sequence
        return self.head(h[-1]).squeeze(-1)

m = Net(); opt = torch.optim.Adam(m.parameters(), lr=0.01); lf = nn.MSELoss()
for ep in range(31):
    perm = torch.randperm(len(Xtr))
    for i in range(0, len(Xtr), 64):
        idx = perm[i:i + 64]
        opt.zero_grad(); lf(m(Xtr[idx]), ytr[idx]).backward(); opt.step()
    if ep % 10 == 0:
        with torch.no_grad():
            print(f"epoch {ep:2d}  test MSE {lf(m(Xte), yte).item():.4f}")
print("baseline 'predict same as last value' MSE:", round(((Xte[:, -1, 0] - yte) ** 2).mean().item(), 4))
print("noise floor (0.05^2):", 0.0025)
```

Output:

```
epoch  0  test MSE 0.0683
epoch 10  test MSE 0.0039
epoch 20  test MSE 0.0031
epoch 30  test MSE 0.0030
baseline 'predict same as last value' MSE: 0.0084
noise floor (0.05^2): 0.0025
```

How to read it:

- Test MSE falls from 0.068 to **0.0030**, close to the unavoidable noise floor of 0.0025 (the noise I added has standard deviation 0.05).
- The naive baseline ("tomorrow = today") scores 0.0084, so the LSTM is almost **3x better** than the sensible dumb guess. Always include such a baseline.
- Caveat: a sine wave is an easy, clean pattern. Real series are far messier, and beating "same as last value" on real data (sales, prices) is genuinely hard.

## Real-world rules of thumb

- **Shape matters:** with `batch_first=True` the input is `(batch, time steps, features)`.
- Use `h[-1]` (the final hidden state) when you want one answer per sequence. Use `out` when you need an output at every step.
- LSTMs/GRUs are great for small and medium sequence problems, and are cheap on CPU. For text and long-range context, **Transformers have mostly replaced them** (next note).
- For tabular time series, a gradient-boosted model with lag features (`value_yesterday`, `rolling_mean_7`) often beats an LSTM. Try it first.
- Scale your series (e.g. standardise) before feeding it in, using training-set statistics only.
- Training can be unstable. Gradient clipping (`torch.nn.utils.clip_grad_norm_`) is a common fix.

## Quick check

Why must a time-series split be ordered in time, not shuffled? *(Shuffling lets the model train on the future to predict the past, which is leakage.)*

Next: [05 Transformers + attention](05-transformers-attention-intuition.md).
