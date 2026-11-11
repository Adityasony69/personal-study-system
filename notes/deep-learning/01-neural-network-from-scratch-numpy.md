# Neural Network from Scratch (NumPy)

Building one by hand once removes the magic. Every framework (PyTorch, TensorFlow) automates exactly what you see here.

## The idea in plain English

A neural network is a stack of small calculations:

```
input  ->  [weights, add bias, squash]  ->  hidden layer  ->  [weights, add bias, squash]  ->  output
```

- A **neuron** takes a weighted sum of its inputs and passes it through an **activation function** (`tanh`, `ReLU`, `sigmoid`).
- The activation is the key. Without it, stacked layers collapse into one big linear model. The bend is what lets networks learn curves.
- **Forward pass:** push data through to get a prediction.
- **Loss:** score how wrong it is (here, log loss from the machine-learning notes).
- **Backward pass (backpropagation):** use the chain rule to work out how each weight contributed to the error.
- **Update:** nudge every weight a little in the direction that reduces the error (gradient descent).

## Code: learn two interleaved half-moons

A straight line cannot separate this data, so a linear model fails and a hidden layer is needed.

```python
import numpy as np
from sklearn.datasets import make_moons
np.random.seed(0)
X, y = make_moons(400, noise=0.2, random_state=0)
y = y.reshape(-1, 1)

H = 16                                   # hidden neurons
W1 = np.random.randn(2, H) * 0.5; b1 = np.zeros((1, H))
W2 = np.random.randn(H, 1) * 0.5; b2 = np.zeros((1, 1))
sigmoid = lambda z: 1 / (1 + np.exp(-z))
lr = 0.5
for epoch in range(2001):
    # forward pass
    a1 = np.tanh(X @ W1 + b1)
    p = sigmoid(a1 @ W2 + b2)
    loss = -np.mean(y * np.log(p + 1e-9) + (1 - y) * np.log(1 - p + 1e-9))
    # backward pass (chain rule, layer by layer)
    dz2 = (p - y) / len(X)
    dW2 = a1.T @ dz2;  db2 = dz2.sum(0, keepdims=True)
    dz1 = (dz2 @ W2.T) * (1 - a1 ** 2)
    dW1 = X.T @ dz1;   db1 = dz1.sum(0, keepdims=True)
    # update
    W1 -= lr * dW1; b1 -= lr * db1; W2 -= lr * dW2; b2 -= lr * db2
    if epoch % 400 == 0:
        print(f"epoch {epoch:4d}  loss {loss:.4f}  accuracy {((p > 0.5) == y).mean():.3f}")
```

Output:

```
epoch    0  loss 0.6259  accuracy 0.645
epoch  400  loss 0.1584  accuracy 0.940
epoch  800  loss 0.1135  accuracy 0.960
epoch 1200  loss 0.1014  accuracy 0.963
epoch 1600  loss 0.0964  accuracy 0.963
epoch 2000  loss 0.0938  accuracy 0.963
```

The loss falls from 0.63 to 0.09 and accuracy climbs from 64.5% to 96.3%. Note this accuracy is on the **training** data. It shows the network *can learn* the shape; it isn't a claim about unseen data (the next note uses a proper test set).

## Reading the backward pass

- `dz2 = (p - y) / N`: for sigmoid + log loss, the error signal simplifies to "prediction minus truth". Neat and worth remembering.
- `dz1 = (dz2 @ W2.T) * (1 - a1**2)`: pass the error back through `W2`, then multiply by the slope of `tanh` (`1 - tanh²`). That's the chain rule.
- Each gradient has the same shape as its weight. When shapes don't match, you have a bug.

## Real-world rules of thumb

- **You will never write this in a job.** PyTorch's autograd does it. The value is knowing what `loss.backward()` does, so errors like exploding losses make sense.
- Initialise weights small and random, never all zeros (every neuron would learn the same thing).
- If the loss goes `nan`, your learning rate is too high.
- A way to sanity-check your gradients: nudge one weight slightly and see if the loss changes by what the gradient predicts.
- More hidden neurons = more capacity = more risk of overfitting. Always evaluate on held-out data.

## Quick check

Why do we need an activation function like `tanh` between layers? *(Without it, many layers are mathematically the same as one linear layer.)*

Next: [02 PyTorch basics](02-pytorch-basics.md).
