# Logistic Regression + Log Loss

**What it's for:** yes/no questions. Will this customer churn? Is this email spam? Is the transaction fraud? Despite the name, it's a *classifier*, not a regression.

## The idea in plain English

Linear regression can output any number, such as -40 or 900. A probability must sit between 0 and 1. Logistic regression takes the same weighted sum as linear regression and squashes it through the **sigmoid** function, an S-curve that maps any number into 0 to 1.

```
probability = sigmoid(w1*x1 + w2*x2 + ... + b)
```

Then you pick a threshold (usually 0.5): above it predict "yes", below it predict "no".

## Log loss: how the model is graded

Accuracy only asks "right or wrong?". **Log loss** asks "how confident were you, and were you right to be?" It punishes confident wrong answers brutally.

If the true answer is "yes", the penalty is `-log(predicted probability of yes)`:

| Model said P(yes) = | Penalty |
|---|---|
| 0.9 (confident, right) | 0.11 |
| 0.6 (unsure, right) | 0.51 |
| 0.1 (confident, **wrong**) | 2.30 |

Being confidently wrong costs about 20 times more than being confidently right. This is why log loss is the training objective: it forces honest probabilities, not just correct labels.

## Code

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import log_loss, accuracy_score
X, y = make_classification(n_samples=1000, n_features=5, random_state=0)
Xtr, Xte, ytr, yte = train_test_split(X, y, random_state=0)
m = LogisticRegression().fit(Xtr, ytr)
p = m.predict_proba(Xte)[:, 1]
print("accuracy", round(accuracy_score(yte, p > 0.5), 3))
print("sklearn log loss", round(log_loss(yte, p), 4))
manual = -np.mean(yte * np.log(p) + (1 - yte) * np.log(1 - p))
print("manual  log loss", round(manual, 4))
for conf in (0.9, 0.6, 0.1):  # true label is 1
    print(f"predicted P(1)={conf}: penalty {-np.log(conf):.2f}")
```

Output:

```
accuracy 0.96
sklearn log loss 0.1792
manual  log loss 0.1792
predicted P(1)=0.9: penalty 0.11
predicted P(1)=0.6: penalty 0.51
predicted P(1)=0.1: penalty 2.30
```

The hand-written formula matches scikit-learn exactly. Lower is better, and 0 is perfect.

## Real-world rules of thumb

- Use `predict_proba`, not just `predict`. Probabilities let you rank customers, set your own threshold and see uncertainty.
- **The 0.5 threshold is a choice.** For fraud or cancer screening you'd lower it to catch more positives, and accept more false alarms. See [05 Model evaluation](05-model-evaluation.md).
- Scale features first (`StandardScaler`). `LogisticRegression` applies L2 regularisation by default, which only behaves well on scaled data.
- The coefficients are interpretable: positive pushes toward "yes", negative toward "no". That's why banks and hospitals still use it.
- It's a strong baseline. Always try it before anything fancier. If a random forest barely beats it, ship the logistic regression.

## Quick check

A model gives P(fraud) = 0.01 on a transaction that really was fraud. Is that a small or large log loss? *(Large: `-log(0.01)` is about 4.6.)*
