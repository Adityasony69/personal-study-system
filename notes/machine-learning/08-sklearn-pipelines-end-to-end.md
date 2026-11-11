# scikit-learn Pipelines, End to End

A **Pipeline** chains preprocessing and the model into one object. It's the single most useful habit in practical scikit-learn, because it:

- prevents data leakage (preprocessing is refit inside each CV fold, see [06](06-feature-engineering-data-leakage.md)),
- lets you tune preprocessing and model settings together,
- saves as one file, so production gets *exactly* the same steps as training.

## The pieces

- `Pipeline([...])`: run steps in order, the last being the model.
- `ColumnTransformer`: apply different steps to different columns (numbers vs categories).
- `SimpleImputer`: fill missing values.
- `OneHotEncoder(handle_unknown="ignore")`: turn categories into columns, and don't crash on a category never seen in training.
- `GridSearchCV`: try settings with cross-validation. Use `step__param` names such as `model__max_depth`.

## Full example: predict customer churn from messy data

```python
import pandas as pd, numpy as np, joblib
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
rng = np.random.default_rng(0); n = 800
df = pd.DataFrame({"age": rng.integers(18, 70, n).astype(float), "income": rng.normal(50000, 15000, n),
                   "plan": rng.choice(["basic", "pro", "team"], n), "city": rng.choice(["Pune", "Delhi", "Goa"], n)})
df["churn"] = (((df.income < 45000) & (df.plan == "basic")) | (rng.random(n) < 0.05)).astype(int)
df.loc[rng.choice(n, 60, replace=False), "age"] = np.nan          # 60 missing ages
X, y = df.drop(columns="churn"), df.churn
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=0)

pre = ColumnTransformer([
 ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), ["age", "income"]),
 ("cat", OneHotEncoder(handle_unknown="ignore"), ["plan", "city"])])
pipe = Pipeline([("pre", pre), ("model", RandomForestClassifier(random_state=0))])

gs = GridSearchCV(pipe, {"model__n_estimators": [50, 200], "model__max_depth": [3, None]}, cv=5).fit(Xtr, ytr)
print("best:", gs.best_params_, "cv", gs.best_score_.round(3), "test", round(gs.score(Xte, yte), 3))

joblib.dump(gs.best_estimator_, "model.joblib")
new = pd.DataFrame([{"age": None, "income": 30000, "plan": "basic", "city": "Mars"}])  # messy raw input
print("reloaded predict_proba:", joblib.load("model.joblib").predict_proba(new).round(3))
```

Output:

```
best: {'model__max_depth': 3, 'model__n_estimators': 50} cv 0.945 test 0.945
reloaded predict_proba: [[0.453 0.547]]
```

What to notice:

- The CV score (0.945) and the final test score (0.945) agree. That's what you want: no leak, no surprise.
- The saved model accepted a **raw row with a missing age and an unseen city ("Mars")** and still returned a probability. The imputer and encoder travel inside the file. That robustness is the whole point.
- Honest caveat: the two accuracy numbers are equal here by coincidence, and the data is synthetic, so this tells you the *plumbing* works, not that churn is this easy to predict.

## Real-world rules of thumb

- **Never preprocess outside the pipeline** and then cross-validate. That's the leak from note 06.
- Save the whole pipeline with `joblib.dump`, not just the model. Only load `.joblib` files you created yourself or trust, because loading one can run code.
- Pin the scikit-learn version used for training. A model saved on one version may not load on another.
- Use `pipe.named_steps` and `get_feature_names_out()` to inspect what happened inside.
- Pass a DataFrame with the same column names in production. `ColumnTransformer` selects by name.
- Grid search grows fast: 2 x 2 settings x 5 folds = 20 fits. Use `RandomizedSearchCV` for bigger spaces.

## Checklist for any new ML project

1. Define the target and the metric that matters ([05](05-model-evaluation.md)).
2. Split off a test set, and don't touch it.
3. Build a baseline (`DummyClassifier`, then logistic regression).
4. Build a pipeline: impute, encode, scale, model.
5. Cross-validate; compare a forest or boosting model ([04](04-random-forests-gradient-boosting.md)).
6. Tune with `GridSearchCV`, check the test set once, save the pipeline.

## Quick check

Why save the pipeline instead of just the model? *(The model alone expects already-processed numbers; the pipeline accepts raw data and repeats the exact same preprocessing.)*
