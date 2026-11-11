# Feature Engineering + Data Leakage

Feature engineering is turning raw columns into inputs a model can use well. Data leakage is the silent mistake that makes a model look brilliant in testing and fail in production. Real projects spend more time here than on choosing algorithms.

## Feature engineering: common moves

| Raw data | Better feature | Why |
|---|---|---|
| Date | month, day of week, "days since signup" | models can't read a date string |
| Category (`city`) | one-hot columns | models need numbers, not text |
| Total spend + order count | `avg_order = spend / orders` | a ratio can matter more than either part |
| Skewed money (120 to 5000) | `log1p(spend)` | tames huge outliers |
| Missing values | impute (median) and maybe a "was missing" flag | most models crash on NaN |

```python
import numpy as np, pandas as pd
df = pd.DataFrame({"signup": pd.to_datetime(["2026-01-05", "2026-03-20", "2026-06-11"]),
                   "city": ["Pune", "Delhi", "Pune"], "spend": [120.0, 5000.0, 90.0], "orders": [4, 20, 3]})
df["signup_month"] = df.signup.dt.month
df["signup_dow"] = df.signup.dt.dayofweek
df["avg_order"] = df.spend / df.orders
df["log_spend"] = np.log1p(df.spend)
print(pd.get_dummies(df.drop(columns="signup"), columns=["city"]).round(2).to_string())
```

Output:

```
    spend  orders  signup_month  signup_dow  avg_order  log_spend  city_Delhi  city_Pune
0   120.0       4             1           0       30.0       4.80       False       True
1  5000.0      20             3           4      250.0       8.52        True      False
2    90.0       3             6           3       30.0       4.51       False       True
```

## Data leakage: the model peeks at the answers

Leakage means information from outside the training data (usually from the test set or the future) sneaks into training. The scores look amazing, then reality is a disappointment.

Common forms:

1. **Preprocessing on all the data** before splitting: scaling, imputing, or selecting features using test rows.
2. **A feature that is really the answer in disguise**: e.g. `refund_issued` when predicting churn, or `discharge_notes` when predicting diagnosis.
3. **Future information**: using next month's data to predict next month.
4. **Duplicates** across train and test (the same customer twice).

### Demo: leakage on pure noise

Here the data is 2000 random columns and random labels. There is **nothing to learn**; the honest accuracy is 50%.

```python
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.pipeline import make_pipeline
rng = np.random.default_rng(0)
X = rng.normal(size=(100, 2000)); y = rng.integers(0, 2, 100)
Xs = SelectKBest(f_classif, k=10).fit_transform(X, y)        # picks the "best" 10 using ALL labels
print("LEAKY  (select then CV):", cross_val_score(LogisticRegression(), Xs, y, cv=5).mean().round(3))
safe = make_pipeline(SelectKBest(f_classif, k=10), LogisticRegression())   # selection inside each fold
print("CLEAN  (select in pipeline):", cross_val_score(safe, X, y, cv=5).mean().round(3))
```

Output:

```
LEAKY  (select then CV): 0.82
CLEAN  (select in pipeline): 0.58 (truth: coin flip = 0.5)
```

The leaky version "found" an 82% accurate model in pure noise. Choosing the 10 best columns *using all the labels* means the test rows already voted on which features to keep. Inside a pipeline, selection happens only on each fold's training part, and the score falls to roughly a coin flip (0.58 on 100 rows is within noise of 0.5).

## How to avoid leakage

- **Split first, then do everything else.** Fit scalers, imputers, encoders and selectors on the training part only.
- **Put preprocessing inside a `Pipeline`** so cross-validation refits it per fold automatically. See [08 Pipelines](08-sklearn-pipelines-end-to-end.md).
- For every feature ask: "Would I actually know this at the moment I need to make the prediction?"
- Be suspicious of results that look too good. 99% on a hard problem is usually a leak, not genius.
- Split time-based data by time. Group by customer or patient if one entity has many rows.

## Quick check

You standardise the whole dataset, then split into train and test. Is that leakage? *(Yes, a mild one: the test rows influenced the mean and standard deviation. Fit the scaler on train only.)*
