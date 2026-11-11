# PyTorch Basics (Tensors, Autograd, Training Loop)

PyTorch is the most widely used deep-learning library. Three ideas cover 90% of it.

## 1. Tensors

A **tensor** is a NumPy array that can live on a GPU and remember how it was computed. Same maths, same shapes.

## 2. Autograd

Mark a value with `requires_grad=True` and PyTorch records every operation on it. Call `.backward()` and it fills in `.grad` with the derivative. This replaces the hand-written backward pass from [note 01](01-neural-network-from-scratch-numpy.md).

## 3. The training loop

Every PyTorch training loop is the same five lines: zero grads, forward, loss, backward, step.

## Code (torch 2.15, CPU)

```python
import torch, torch.nn as nn
from sklearn.datasets import make_moons
from sklearn.model_selection import train_test_split
torch.manual_seed(0)

# 1. tensors
a = torch.tensor([[1., 2.], [3., 4.]])
print("tensor ops:", (a @ a).tolist(), "| shape", tuple(a.shape), "| mean", a.mean().item())

# 2. autograd: PyTorch computes derivatives for you
w = torch.tensor(3.0, requires_grad=True)
loss = (w * 2 - 10) ** 2          # minimum at w = 5
loss.backward()
print("d(loss)/dw =", w.grad.item(), " (by hand: 2*(2w-10)*2 = 2*(-4)*2 = -16)")

# 3. the standard training loop
X, y = make_moons(1000, noise=0.2, random_state=0)
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0)
Xtr, Xte = torch.tensor(Xtr, dtype=torch.float32), torch.tensor(Xte, dtype=torch.float32)
ytr, yte = torch.tensor(ytr, dtype=torch.float32).unsqueeze(1), torch.tensor(yte, dtype=torch.float32).unsqueeze(1)

model = nn.Sequential(nn.Linear(2, 16), nn.ReLU(), nn.Linear(16, 16), nn.ReLU(), nn.Linear(16, 1))
loss_fn = nn.BCEWithLogitsLoss()
opt = torch.optim.Adam(model.parameters(), lr=0.01)
for epoch in range(201):
    opt.zero_grad()                 # clear old gradients
    loss = loss_fn(model(Xtr), ytr) # forward + loss
    loss.backward()                 # backward
    opt.step()                      # update weights
    if epoch % 50 == 0:
        model.eval()
        with torch.no_grad():
            acc = ((model(Xte) > 0) == yte).float().mean().item()
        model.train()
        print(f"epoch {epoch:3d}  train loss {loss.item():.4f}  test acc {acc:.3f}")
torch.save(model.state_dict(), "m.pt")
print("params:", sum(p.numel() for p in model.parameters()))
```

Output:

```
tensor ops: [[7.0, 10.0], [15.0, 22.0]] | shape (2, 2) | mean 2.5
d(loss)/dw = -16.0  (by hand: 2*(2w-10)*2 = 2*(-4)*2 = -16)
epoch   0  train loss 0.6992  test acc 0.532
epoch  50  train loss 0.2114  test acc 0.896
epoch 100  train loss 0.1098  test acc 0.932
epoch 150  train loss 0.0902  test acc 0.960
epoch 200  train loss 0.0851  test acc 0.960
params: 337
```

Autograd got `-16.0`, matching the hand calculation. The model reaches 96% on **held-out** test data with only 337 parameters.

## The five lines, explained

| Line | What it does | If you forget it |
|---|---|---|
| `opt.zero_grad()` | wipe last step's gradients | gradients **accumulate** and training goes wrong silently |
| `model(X)` | forward pass | n/a |
| `loss_fn(...)` | score the predictions | n/a |
| `loss.backward()` | compute gradients | weights never change |
| `opt.step()` | apply the update | same |

## Real-world rules of thumb

- **`model.eval()` + `torch.no_grad()` when testing.** `eval()` switches off dropout and similar training-only behaviour; `no_grad()` saves memory. Switch back with `model.train()`.
- Use `BCEWithLogitsLoss` (binary) or `CrossEntropyLoss` (multi-class) and feed them **raw scores (logits)**, not probabilities. They apply the sigmoid/softmax internally, which is more numerically stable. That's why the model above has no final sigmoid.
- **Adam** with `lr=0.001` to `0.01` is a good default optimiser.
- Real data goes through mini-batches (e.g. 64 rows at a time) rather than the whole set, as the next notes do.
- Move to GPU with `.to("cuda")` on both the model and the data. Everything here ran fine on CPU.
- Save with `state_dict()` (just the weights) and rebuild the same model class to load. Only load checkpoint files you trust.
- Shape errors are the #1 bug. Print `tensor.shape` constantly.

## Quick check

What happens if you call `loss.backward()` twice without `zero_grad()`? *(The gradients add up, so the update is wrong.)*

Next: [03 CNNs for images](03-cnns-for-images.md).
