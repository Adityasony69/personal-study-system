# Linear Regression from Scratch (Gradient Descent)

**What it's for:** predicting a number (price, delivery time, sales) from other numbers. It's the simplest model there is, and gradient descent, the way it learns, is the same engine behind neural networks.

## The idea in plain English

The model is a straight line: `prediction = w * feature + b`.

- `w` (weight) is the slope: how much the prediction moves per unit of the feature.
- `b` (bias) is where the line starts.

Training means finding the `w` and `b` that make the predictions least wrong.

1. Start with a bad guess (`w=0, b=0`).
2. Measure how wrong you are. The usual measure is **MSE**: square each error, then average. Squaring stops positive and negative errors cancelling out and punishes big misses.
3. Work out which direction to nudge `w` and `b` to reduce the error. That direction is the **gradient**.
4. Take a small step that way. The step size is the **learning rate**.
5. Repeat.

Think of walking downhill in fog: you can't see the valley, but you can feel the slope under your feet.

## Code (run with numpy 2.5 and scikit-learn 1.9)

```python
import numpy as np
rng = np.random.default_rng(0)
size = rng.uniform(500, 2500, 200)                 # sq ft
price = 50 + 0.12 * size + rng.normal(0, 15, 200)  # price in $1000s
x = (size - size.mean()) / size.std()              # scale features!
w, b, lr = 0.0, 0.0, 0.1
for step in range(201):
    pred = w * x + b
    err = pred - price
    loss = (err ** 2).mean()
    w -= lr * 2 * (err * x).mean()
    b -= lr * 2 * err.mean()
    if step in (0, 1, 2, 5, 10, 20, 50, 200):
        print(f"step {step:3d}  loss {loss:9.2f}  w {w:6.2f}  b {b:6.2f}")
from sklearn.linear_model import LinearRegression
m = LinearRegression().fit(x.reshape(-1, 1), price)
print("sklearn:", round(m.coef_[0], 2), round(m.intercept_, 2))
print("predict 1800 sq ft:", round(w * (1800 - size.mean()) / size.std() + b, 1), "k")
```

Output:

```
step   0  loss  62026.07  w  14.24  b  47.63
step   1  loss  39781.10  w  25.63  b  85.74
step   2  loss  25544.32  w  34.74  b 116.23
step   5  loss   6869.30  w  52.52  b 175.74
step  10  loss    946.89  w  65.07  b 217.71
step  20  loss    242.70  w  70.52  b 235.97
step  50  loss    234.48  w  71.18  b 238.17
step 200  loss    234.48  w  71.18  b 238.17
sklearn: 71.18 238.17
predict 1800 sq ft: 264.2 k
```

What to notice:

- The loss drops fast, then flattens at about 234. That's **convergence**. The floor isn't zero because I added noise with a standard deviation of 15, and 15² = 225. The model can't beat the noise.
- Our from-scratch `w` and `b` match scikit-learn to two decimals. That's your proof it works.
- The true relationship is `50 + 0.12*size`. At 1800 sq ft that's 266, and we predicted 264.2 from noisy data. Good.
- `w=71` looks nothing like `0.12` because we standardised `x` (subtracted the mean, divided by the standard deviation). It now means "price rises by 71k for each standard deviation of size".

## Real-world rules of thumb

- **Always scale your features** before gradient descent. With raw square feet (500 to 2500) and a bigger learning rate the steps overshoot and the loss explodes.
- **Learning rate too big:** loss goes up or turns into `nan`. **Too small:** it takes forever. Try 0.1, 0.01, 0.001.
- **Plot the loss curve.** It should fall smoothly. If it doesn't, the learning rate is almost always the culprit.
- In production you'd use `LinearRegression` (it solves the problem directly, no loop). Gradient descent matters because everything bigger (logistic regression, neural nets) uses it.
- Linear models can't see curves or interactions unless you add features such as `size**2`. See [06 Feature engineering](06-feature-engineering-data-leakage.md).

## Quick check

Why does the loss stop at about 234 instead of 0? *(Answer: the data has random noise nobody can predict.)*
